#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <memory>
#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <vector>
#include <math.h>

#include "gradientMex.hpp"
#include "feature_maps.hpp"

using namespace boost::python;
using namespace std;

#define PI 3.14159265f

namespace template_match
{
	struct Line2DParameters
	{
		int numQuantizations = 8;
		double threshold = 5.0;
		bool useGaussian = true;
		int tau = 8;
	};

	class Line2D
	{
	public:
		typedef double T; // set precision here double or float

		Line2D(Line2DParameters paras)
			: _NUM_ORIENTS(paras.numQuantizations),
			_THRESHOLD(paras.threshold),
			_USE_GAUSSIAN(paras.useGaussian),
			_TAU(paras.tau)
		{
		}

		void test(const cv::Mat& image)
		{
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

			cv::Mat map(image.size(), CV_32SC1);

			computeBinaryMap(bins, map);

			cout << map << endl;
		}

		void test2()
		{
			cout << findCosMax(195, 8) << endl;
		}
		
	private:
		void generateLookupTable()
		{
			const int size = (1 << _TAU) - 1;

			// allocate space for table
			_lookupTable.reserve(size * _TAU);


		}

		// the world's worst function
		// it's okay, computed offline :p
		T findCosMax(int cell, int bin)
		{
			bool* a = new bool[_TAU];
			T max = 0;

			for (int i = _TAU - 1; i >= 0; --i)
				a[i] = (cell >> i) & 1;
			
			for (int i = 0; i < _TAU; ++i) {
				if (a[i]) {
					T similarity;
					similarity = (1 << i) * _radsPerBin;
					similarity = abs(cos(similarity - (bin * _radsPerBin)));

					if (similarity > max)
						max = similarity;
				}
			}

			delete[] a;

			return max;
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
		const T _THRESHOLD;
		const bool _USE_GAUSSIAN;
		const int _TAU;

		vector<int> _lookupTable;
		const T _radsPerBin = PI / _NUM_ORIENTS;
	};
}

#endif