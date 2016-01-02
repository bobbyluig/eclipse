#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <memory>
#include <iostream>
#include <fstream>

#include "gradientMex.hpp"

using namespace boost::python;

namespace template_match
{
	struct Line2DParameters
	{
		int numQuantizations = 8;
	};

	class Line2D
	{
	public:
		typedef float T; // set precision here double or float

		Line2D(Line2DParameters paras)
			: _NUM_QUANTS(paras.numQuantizations)
		{

		}

		void test(const cv::Mat& image)
		{
			cv::imshow("Test", image);
		}
		
	private:
		typedef void(*cvOriPtr)
			(const cv::Mat& img, int binSize);
		cvOriPtr cvOri = 0;

		const int _NUM_QUANTS;
	};
}

#endif