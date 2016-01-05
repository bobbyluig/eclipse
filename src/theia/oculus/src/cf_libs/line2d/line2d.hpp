#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <memory>
#include <chrono>
#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <vector>
#include <math.h>

#include "linemod.hpp"

using namespace boost::python;
using namespace std;

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
		}

		void test(const cv::Mat& image, const cv::Mat& templ)
		{
		}

		void test2(const cv::Mat& image, const cv::Mat& templ)
		{
			cv::Ptr<cv::linemod::Detector> detector;
			detector = cv::linemod::getDefaultLINE();

			vector<cv::Mat> sources;
			vector<cv::Mat> templates;
			sources.push_back(image);
			templates.push_back(templ);

			detector->addTemplate(templates, "test1", cv::Mat());
			detector->addTemplate(templates, "test2", cv::Mat());

			// perform matching
			vector<cv::linemod::Match> matches;

			auto start = std::chrono::high_resolution_clock::now();
			detector->match(sources, 80, matches);
			auto elapsed = std::chrono::high_resolution_clock::now() - start;

			long long microseconds = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();

			cout << microseconds << endl;
			cout << matches.size();
		}

	private:
		const int _NUM_ORIENTS;
		const float _THRESHOLD;
		const bool _USE_GAUSSIAN;
		const int _TAU;

		cv::Mat _lookupTable;
		const float _radsPerBin = PI / _NUM_ORIENTS;
	};
}

#endif