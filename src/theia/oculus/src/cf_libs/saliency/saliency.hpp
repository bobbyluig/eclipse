#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/saliency.hpp>

#include <memory>
#include <chrono>
#include <iostream>
#include <fstream>
#include <vector>

using namespace boost::python;
using namespace std;

namespace saliency
{
	class Saliency
	{
	public:
		Saliency(const int width, const int height)
			: _WIDTH(width),
			_HEIGHT(height)
		{
			initialize();
		}

		cv::Mat compute(const cv::Mat& image)
		{
			cv::Mat saliencyMap;
			_saliencyAlgorithm->computeSaliency(image, saliencyMap);
			return saliencyMap;
		}

	private:
		void initialize()
		{
			_saliencyAlgorithm = cv::saliency::Saliency::create("BinWangApr2014");
			_saliencyAlgorithm.dynamicCast<cv::saliency::MotionSaliencyBinWangApr2014>()->setImagesize(_WIDTH, _HEIGHT);
			_saliencyAlgorithm.dynamicCast<cv::saliency::MotionSaliencyBinWangApr2014>()->init();
		}

		cv::Ptr<cv::saliency::Saliency> _saliencyAlgorithm;

		const int _WIDTH;
		const int _HEIGHT;
	};
}

#endif