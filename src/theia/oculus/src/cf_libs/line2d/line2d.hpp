#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <inpaint/template_match_candidates.h>

#include <memory>
#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <vector>
#include <math.h>

#include "gradientMex.hpp"

using namespace boost::python;
using namespace std;
using namespace Inpaint;

#define PI 3.14159265f

namespace template_match
{
	struct Line2DParameters
	{
		int numQuantizations = 8;
		float threshold = 5.0;
		bool useGaussian = true;
		int tau = 8;
	};

	class Line2D
	{
	public:
		Line2D(Line2DParameters paras)
			: _NUM_ORIENTS(paras.numQuantizations),
			_THRESHOLD(paras.threshold),
			_USE_GAUSSIAN(paras.useGaussian),
			_TAU(paras.tau)
		{
			generateLookupTable();
		}

		void test(const cv::Mat& image, const cv::Mat& templ)
		{
			//image
			cv::Mat floatImage;
			image.convertTo(floatImage, CV_32FC3);

			cv::Mat bins(image.size(), CV_32SC1);

			if (_USE_GAUSSIAN) {
				cv::GaussianBlur(floatImage, floatImage, cv::Size(11, 11), 0);
				cvOriNone(floatImage, reinterpret_cast<int*>(bins.data), _NUM_ORIENTS);
			}
			else {
				cvOri(floatImage, reinterpret_cast<int*>(bins.data), _NUM_ORIENTS);
			}
			
			// cv::Mat map(image.size(), CV_32SC1);
			// computeBinaryMap(bins, map);

			// cv::Mat* responseMap = new cv::Mat[_NUM_ORIENTS];
			// computeResponseMap(map, responseMap);

			// template
			cv::Mat floatTemplate;
			templ.convertTo(floatTemplate, CV_32FC3);

			cv::Mat templBins(templ.size(), CV_32SC1);

			cv::GaussianBlur(floatTemplate, floatTemplate, cv::Size(11, 11), 0);
			cvOriNone(floatTemplate, reinterpret_cast<int*>(templBins.data), _NUM_ORIENTS);

			// output
			// cv::Mat output(image.size(), CV_32FC1);
			// compare(responseMap, templBins, output);

			bins.convertTo(bins, CV_8U);
			templBins.convertTo(templBins, CV_8U);

			cv::Mat result;
			cv::matchTemplate(bins, templBins, result, CV_TM_CCOEFF_NORMED);

			cv::imshow("map", result);
		}

		void test2(const cv::Mat& image, const cv::Mat& templ)
		{
			cv::Mat dst;
			fastMatchTemplate(image, templ, dst, 3);
			cv::imshow("fast", dst);
		}
		
	private:
		void fastMatchTemplate(const cv::Mat& srca,  // The reference image
			const cv::Mat& srcb,  // The template image
			cv::Mat& dst,   // Template matching result
			int maxlevel)   // Number of levels
		{
			std::vector<cv::Mat> refs, tpls, results;

			// Build Gaussian pyramid
			cv::buildPyramid(srca, refs, maxlevel);
			cv::buildPyramid(srcb, tpls, maxlevel);

			cv::Mat ref, tpl, res;

			// Process each level
			for (int level = maxlevel; level >= 0; level--)
			{
				ref = refs[level];
				tpl = tpls[level];
				res = cv::Mat::zeros(ref.size() + cv::Size(1, 1) - tpl.size(), CV_32FC1);

				if (level == maxlevel)
				{
					// On the smallest level, just perform regular template matching
					cv::matchTemplate(ref, tpl, res, CV_TM_CCOEFF_NORMED);
				}
				else
				{
					// On the next layers, template matching is performed on pre-defined 
					// ROI areas.  We define the ROI using the template matching result 
					// from the previous layer.

					cv::Mat mask;
					cv::pyrUp(results.back(), mask);

					cv::Mat mask8u;
					mask.convertTo(mask8u, CV_8U);

					// Find matches from previous layer
					std::vector<std::vector<cv::Point> > contours;
					cv::findContours(mask8u, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);

					// Use the contours to define region of interest and 
					// perform template matching on the areas
					for (int i = 0; i < contours.size(); i++)
					{
						cv::Rect r = cv::boundingRect(contours[i]);
						cv::matchTemplate(
							ref(r + (tpl.size() - cv::Size(1, 1))),
							tpl,
							res(r),
							CV_TM_CCORR_NORMED
							);
					}
				}

				// Only keep good matches
				cv::threshold(res, res, 0.8, 1., CV_THRESH_TOZERO);
				results.push_back(res);
			}

			res.copyTo(dst);
		}

		void compare(cv::Mat* responseMap, cv::Mat& templateBins, cv::Mat& output) {
			const int width = templateBins.cols;
			const int height = templateBins.rows;

			for (int i = 0; i < output.rows - height; ++i) {
				for (int j = 0; j < output.cols - width; ++j) {
					float score = 0;

					for (int tH = 0; tH < templateBins.rows; ++tH) {
						for (int tW = 0; tW < templateBins.cols; ++tW) {
							if (templateBins.at<int>(tH, tW) != 0)
								score += responseMap[templateBins.at<int>(tH, tW) - 1].at<float>(i + tH, j + tW);
						}
					}

					output.at<float>(i, j) = score / width / height;
				}
			}
		}

		// populate lookup table
		// each row is a new bin
		void generateLookupTable()
		{
			const int cols = 1 << _NUM_ORIENTS;

			// allocate space for table
			_lookupTable = cv::Mat(_NUM_ORIENTS, cols, CV_32FC1);

			for (int row = 0; row < _NUM_ORIENTS; ++row) {
				for (int col = 0; col < cols; ++col) {
					_lookupTable.at<float>(row, col) = findCosMax(col, row + 1);
				}
			}
		}

		// the world's worst function
		// it's okay, computed offline :p
		float findCosMax(int cell, int bin)
		{
			bool* a = new bool[_NUM_ORIENTS];
			float max = 0;

			for (int i = _NUM_ORIENTS - 1; i >= 0; --i)
				a[i] = (cell >> i) & 1;
			
			for (int i = 0; i < _NUM_ORIENTS; ++i) {
				if (a[i]) {
					float similarity;
					similarity = (1 << i) * _radsPerBin;
					similarity = abs(cos(similarity - (bin * _radsPerBin)));

					if (similarity > max)
						max = similarity;
				}
			}

			delete[] a;

			return max;
		}

		void computeResponseMap(cv::Mat& in, cv::Mat* outArray)
		{
			const int width = 1 << _NUM_ORIENTS;

			for (int bin = 0; bin < _NUM_ORIENTS; ++bin) {
				outArray[bin] = cv::Mat(in.size(), CV_32FC1);

				for (int i = 0; i < in.cols * in.rows; ++i) {
					outArray[bin].at<float>(i) = _lookupTable.at<float>(bin, in.at<int>(i));
				}
			}

		}

		void computeBinaryMap(cv::Mat& bins, cv::Mat& out)
		{
			CV_Assert(out.channels() == 1);

			// compute binary map
			for (int i = 0; i < bins.cols * bins.rows; ++i)
				bins.at<int>(i) = (1 << bins.at<int>(i)) >> 1;

			// spread binary map
			const int shifts = _TAU / 2;
			out = bins.clone();

			// shift the image and OR
			for (int i = -shifts; i <= shifts; ++i) {
				for (int j = -shifts; j <= shifts; ++j) {
					cv::Mat mask = translateImg(bins, i, j);
					cv::bitwise_or(mask, out, out);
				}
			}
		}

		cv::Mat translateImg(cv::Mat &img, int shiftCol, int shiftRow) {
			cv::Mat out = cv::Mat::zeros(img.size(), img.type());
			cv::Rect a = cv::Rect(max(0, -shiftCol), max(0, -shiftRow), img.cols - abs(shiftCol), img.rows - abs(shiftRow));
			cv::Rect b = cv::Rect(max(0, shiftCol), max(0, shiftRow), img.cols - abs(shiftCol), img.rows - abs(shiftRow));
			img(a).copyTo(out(b));
			return out;
		}

		void cvOriNone(const cv::Mat& img, int* out, int nOrients)
		{
			// ensure array is continuous
			const cv::Mat& image = (img.isContinuous() ? img : img.clone());

			const int channels = image.channels();
			const int width = image.cols;
			const int height = image.rows;

			CV_Assert(channels == 3);

			// output arrays must be 4-byte aligned
			float* const M = (float*)alMalloc(width * height * sizeof(float), 16);
			float* const O = (float*)alMalloc(width * height * sizeof(float), 16);

			float* I = (float*)wrCalloc(static_cast<size_t>(width * height * channels), sizeof(float));
			float* imageData = reinterpret_cast<float*>(image.data);
			float* redChannel = I;
			float* greenChannel = I + width * height;
			float* blueChannel = I + 2 * width * height;

			for (int i = 0; i < height * width; ++i)
			{
				blueChannel[i] = imageData[i * 3];
				greenChannel[i] = imageData[i * 3 + 1];
				redChannel[i] = imageData[i * 3 + 2];
			}

			// calc gradient ori in col major - switch width and height
			piotr::gradMag(I, M, O, width, height, 3, false);

			// quantize graidents
			piotr::oriQuantize(O, M, out, width * height, nOrients, (float)_THRESHOLD, false);

			alFree(M);
			alFree(O);
			wrFree(I);
		}

		void cvOri(const cv::Mat& img, int* out, int nOrients)
		{
			// ensure array is continuous
			const cv::Mat& image = (img.isContinuous() ? img : img.clone());

			const int channels = image.channels();
			const int width = image.cols;
			const int height = image.rows;

			CV_Assert(channels == 3);

			// output arrays must be 4-byte aligned
			float* const M = (float*)alMalloc(width * height * sizeof(float), 16);
			float* const O = (float*)alMalloc(width * height * sizeof(float), 16);
			int* const O0 = (int*)alMalloc(width * height * sizeof(int), 16);

			float* I = (float*)wrCalloc(static_cast<size_t>(width * height * channels), sizeof(float));
			float* imageData = reinterpret_cast<float*>(image.data);
			float* redChannel = I;
			float* greenChannel = I + width * height;
			float* blueChannel = I + 2 * width * height;

			for (int i = 0; i < height * width; ++i)
			{
				blueChannel[i] = imageData[i * 3];
				greenChannel[i] = imageData[i * 3 + 1];
				redChannel[i] = imageData[i * 3 + 2];
			}

			// calc gradient ori in col major - switch width and height
			piotr::gradMag(I, M, O, width, height, 3, false);

			// quantize graidents
			piotr::oriQuantize(O, M, O0, width * height, nOrients, (float)_THRESHOLD, false);

			// district voting cycle (3x3), ignoring outer 1px border
			int district[9];

			for (int i = 1; i < height - 1; ++i) {
				for (int j = 1; j < width - 1; ++j) {
					// reset array for voting
					memset(district, 0, sizeof(district));

					district[O0[(i - 1)*width + j - 1]]++;
					district[O0[(i - 1)*width + j]]++;
					district[O0[(i - 1)*width + j + 1]]++;

					district[O0[i*width + j - 1]]++;
					district[O0[i*width + j]]++;
					district[O0[i*width + j + 1]]++;

					district[O0[(i + 1)*width + j - 1]]++;
					district[O0[(i + 1)*width + j]]++;
					district[O0[(i + 1)*width + j + 1]]++;

					for (int k = 0; k < 9; k++) {
						if (district[k] > 4) {
							out[i*width + j] = k;
							break;
						}
					}
				}
			}

			alFree(O0);
			alFree(M);
			alFree(O);
			wrFree(I);
		}

		const int _NUM_ORIENTS;
		const float _THRESHOLD;
		const bool _USE_GAUSSIAN;
		const int _TAU;

		cv::Mat _lookupTable;
		const float _radsPerBin = PI / _NUM_ORIENTS;
		TemplateMatchCandidates _matcher;
	};
}

#endif