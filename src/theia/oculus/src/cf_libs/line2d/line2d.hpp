#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <memory>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>

#include "gradientMex.hpp"

using namespace boost::python;
using namespace std;

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

			int* const out = (int*)alMalloc(image.cols * image.rows * sizeof(int), 16);

			if (_USE_GAUSSIAN) {
				cv::GaussianBlur(floatImage, floatImage, cv::Size(11, 11), 0);
				cvOriNone(floatImage, out, _NUM_ORIENTS);
			}
			else {
				cvOri(floatImage, out, _NUM_ORIENTS);
			}

			cv::Mat display(image.rows, image.cols, CV_32FC1);
			float* cdata = reinterpret_cast<float*>(display.data);

			for (int i = 0; i < image.cols * image.rows; ++i)
				cdata[i] = (float)out[i] / 8.0f;

			cv::imshow("out", display);

			alFree(out);
		}

		void test2()
		{
			int a_data[4] = { 1, 2, 3, 4 };
			int b_data[4] = { 2, 3, 4, 10 };
			cv::Mat a(2, 2, CV_32SC1, a_data);
			cv::Mat b(2, 2, CV_32SC1, b_data);
			cv::Mat c;
			cv::bitwise_or(a, b, c);

			cout << c << endl;
		}
		
	private:
		void computeBinaryMap(int* bins, int* out, const int width, const int height)
		{
			// compute binary map
			for (int i = 0; i < width * height; ++i)
				bins[i] = 2 << bins[i];

			// spread binary map
			int* district = new int[_TAU * _TAU];

			for (int i = 0; i < height - _TAU; ++i) {
				for (int j = 0; j < width - _TAU; ++j) {

				}
			}
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
	};
}

#endif