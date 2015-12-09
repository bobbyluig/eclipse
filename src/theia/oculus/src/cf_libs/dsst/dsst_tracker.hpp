#ifndef DSST_TRACKER_HPP_
#define DSST_TRACKER_HPP_

#include <boost/python.hpp>

#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/core/traits.hpp>
#include <memory>
#include <iostream>
#include <fstream>

#include "cv_ext.hpp"
#include "mat_consts.hpp"
#include "feature_channels.hpp"
#include "gradientMex.hpp"
#include "math_helper.hpp"
#include "scale_estimator.hpp"
#include "psr.hpp"

using namespace boost::python;

namespace cf_tracking
{
	struct DsstParameters
	{
		double padding = static_cast<double>(1.6);
		double outputSigmaFactor = static_cast<double>(0.05);
		double lambda = static_cast<double>(0.01);
		double learningRate = static_cast<double>(0.012);
		int templateSize = 100;
		int cellSize = 2;

		bool enableTrackingLossDetection = false;
		double psrThreshold = 13.5;
		int psrPeakDel = 1;

		bool enableScaleEstimator = true;
		double scaleSigmaFactor = static_cast<double>(0.25);
		double scaleStep = static_cast<double>(1.02);
		int scaleCellSize = 4;
		int numberOfScales = 33;

		//testing
		bool originalVersion = false;
		int resizeType = cv::INTER_LINEAR;
		bool useFhogTranspose = false;
		double minArea = static_cast<double>(10);
		double maxAreaFactor = static_cast<double>(0.8);
		bool useCcs = true;
	};

	class DsstTracker
	{
	public:
		typedef float T; // set precision here double or float
		static const int CV_TYPE = cv::DataType<T>::type;
		typedef cv::Size_<T> Size;
		typedef cv::Point_<T> Point;
		typedef cv::Rect_<T> Rect;
		typedef FhogFeatureChannels<T> FFC;
		typedef DsstFeatureChannels<T> DFC;
		typedef mat_consts::constants<T> consts;
		typedef boost::python::tuple Tuple;

		DsstTracker(DsstParameters paras)
			: _isInitialized(false),
			_scaleEstimator(0),
			_PADDING(static_cast<T>(paras.padding)),
			_OUTPUT_SIGMA_FACTOR(static_cast<T>(paras.outputSigmaFactor)),
			_LAMBDA(static_cast<T>(paras.lambda)),
			_LEARNING_RATE(static_cast<T>(paras.learningRate)),
			_CELL_SIZE(paras.cellSize),
			_TEMPLATE_SIZE(paras.templateSize),
			_PSR_THRESHOLD(static_cast<T>(paras.psrThreshold)),
			_PSR_PEAK_DEL(paras.psrPeakDel),
			_MIN_AREA(static_cast<T>(paras.minArea)),
			_MAX_AREA_FACTOR(static_cast<T>(paras.maxAreaFactor)),
			_ENABLE_TRACKING_LOSS_DETECTION(paras.enableTrackingLossDetection),
			_ORIGINAL_VERSION(paras.originalVersion),
			_RESIZE_TYPE(paras.resizeType),
			_USE_CCS(paras.useCcs)
		{
			if (paras.enableScaleEstimator)
			{
				ScaleEstimatorParas<T> sp;
				sp.scaleCellSize = paras.scaleCellSize;
				sp.scaleStep = static_cast<T>(paras.scaleStep);
				sp.numberOfScales = paras.numberOfScales;
				sp.scaleSigmaFactor = static_cast<T>(paras.scaleSigmaFactor);
				sp.lambda = static_cast<T>(paras.lambda);
				sp.learningRate = static_cast<T>(paras.learningRate);
				sp.useFhogTranspose = paras.useFhogTranspose;
				sp.resizeType = paras.resizeType;
				sp.originalVersion = paras.originalVersion;
				_scaleEstimator = new ScaleEstimator<T>(sp);
			}

			if (paras.useFhogTranspose)
				cvFhog = &piotr::cvFhogT < T, DFC >;
			else
				cvFhog = &piotr::cvFhog < T, DFC >;

			if (_USE_CCS)
				calcDft = &cf_tracking::dftCcs;
			else
				calcDft = &cf_tracking::dftNoCcs;

			// init dft
			cv::Mat initDft = (cv::Mat_<T>(1, 1) << 1);
			calcDft(initDft, initDft, 0);
		}

		~DsstTracker()
		{
			delete _scaleEstimator;
		}

		bool reinit(const cv::Mat& image, Tuple boundingBox)
		{
			Rect bb = Rect(
				extract<T>(boundingBox[0]),
				extract<T>(boundingBox[1]),
				extract<T>(boundingBox[2]),
				extract<T>(boundingBox[3])
				);

			return reinit_(image, bb);
		}

		bool update(const cv::Mat& image)
		{
			Rect bb = Rect(
				position[0],
				position[1],
				position[2],
				position[3]
				);

			if (update_(image, bb) == false)
				return false;

			position[0] = static_cast<T>(bb.x);
			position[1] = static_cast<T>(bb.y);
			position[2] = static_cast<T>(bb.width);
			position[3] = static_cast<T>(bb.height);
			return true;
		}

		bool updateAt(const cv::Mat& image, Tuple boundingBox)
		{
			bool isValid = false;

			Rect bb = Rect(
				extract<T>(boundingBox[0]),
				extract<T>(boundingBox[1]),
				extract<T>(boundingBox[2]),
				extract<T>(boundingBox[3])
				);

			isValid = updateAt_(image, bb);

			position[0] = static_cast<T>(bb.x);
			position[1] = static_cast<T>(bb.y);
			position[2] = static_cast<T>(bb.width);
			position[3] = static_cast<T>(bb.height);

			return isValid;
		}

		Tuple getBoundingBox()
		{
			return boost::python::make_tuple(position[0], position[1], position[2], position[3]);
		}

		Tuple getCenter()
		{
			return boost::python::make_tuple(position[0] + position[2] / 2, position[1] + position[3] / 2);
		}

	private:
		DsstTracker& operator=(const DsstTracker&)
		{}

		bool reinit_(const cv::Mat& image, Rect& boundingBox)
		{
			_pos.x = floor(boundingBox.x) + floor(boundingBox.width * consts::c0_5);
			_pos.y = floor(boundingBox.y) + floor(boundingBox.height * consts::c0_5);
			Size targetSize = Size(boundingBox.width, boundingBox.height);

			_templateSz = Size(floor(targetSize.width * (1 + _PADDING)),
				floor(targetSize.height * (1 + _PADDING)));

			_scale = 1.0;

			if (!_ORIGINAL_VERSION)
			{
				// resize to fixed side length _TEMPLATE_SIZE to stabilize FPS
				if (_templateSz.height > _templateSz.width)
					_scale = _templateSz.height / _TEMPLATE_SIZE;
				else
					_scale = _templateSz.width / _TEMPLATE_SIZE;

				_templateSz = Size(floor(_templateSz.width / _scale), floor(_templateSz.height / _scale));
			}

			_baseTargetSz = Size(targetSize.width / _scale, targetSize.height / _scale);
			_templateScaleFactor = 1 / _scale;

			Size templateSzByCells = Size(floor((_templateSz.width) / _CELL_SIZE),
				floor((_templateSz.height) / _CELL_SIZE));

			// translation filter output target
			T outputSigma = sqrt(_templateSz.area() / ((1 + _PADDING) * (1 + _PADDING)))
				* _OUTPUT_SIGMA_FACTOR / _CELL_SIZE;
			_y = gaussianShapedLabels2D<T>(outputSigma, templateSzByCells);
			calcDft(_y, _yf, 0);

			// translation filter hann window
			cv::Mat cosWindowX;
			cv::Mat cosWindowY;
			cosWindowY = hanningWindow<T>(_yf.rows);
			cosWindowX = hanningWindow<T>(_yf.cols);
			_cosWindow = cosWindowY * cosWindowX.t();

			std::shared_ptr<DFC> hfNum(0);
			cv::Mat hfDen;

			if (getTranslationTrainingData(image, hfNum, hfDen, _pos) == false)
				return false;

			_hfNumerator = hfNum;
			_hfDenominator = hfDen;

			if (_scaleEstimator)
			{
				_scaleEstimator->reinit(image, _pos, targetSize,
					_scale * _templateScaleFactor);
			}

			_lastBoundingBox = boundingBox;
			_isInitialized = true;
			return true;
		}

		bool getTranslationTrainingData(const cv::Mat& image, std::shared_ptr<DFC>& hfNum,
			cv::Mat& hfDen, const Point& pos) const
		{
			std::shared_ptr<DFC> xt(0);

			if (getTranslationFeatures(image, xt, pos, _scale) == false)
				return false;

			std::shared_ptr<DFC> xtf;

			if (_USE_CCS)
				xtf = DFC::dftFeatures(xt);
			else
				xtf = DFC::dftFeatures(xt, cv::DFT_COMPLEX_OUTPUT);

			hfNum = DFC::mulSpectrumsFeatures(_yf, xtf, true);
			hfDen = DFC::sumFeatures(DFC::mulSpectrumsFeatures(xtf, xtf, true));

			return true;
		}

		bool getTranslationFeatures(const cv::Mat& image, std::shared_ptr<DFC>& features,
			const Point& pos, T scale) const
		{
			cv::Mat patch;
			Size patchSize = _templateSz * scale;

			if (getSubWindow(image, patch, patchSize, pos) == false)
				return false;

			if (_ORIGINAL_VERSION)
				depResize(patch, patch, _templateSz);
			else
				resize(patch, patch, _templateSz, 0, 0, _RESIZE_TYPE);

			cv::Mat floatPatch;
			patch.convertTo(floatPatch, CV_32FC(3));

			features.reset(new DFC());
			cvFhog(floatPatch, features, _CELL_SIZE, DFC::numberOfChannels() - 1);

			// append gray-scale image
			if (patch.channels() == 1)
			{
				if (_CELL_SIZE != 1)
					resize(patch, patch, features->channels[0].size(), 0, 0, _RESIZE_TYPE);

				features->channels[DFC::numberOfChannels() - 1] = patch / 255.0 - 0.5;
			}
			else
			{
				if (_CELL_SIZE != 1)
					resize(patch, patch, features->channels[0].size(), 0, 0, _RESIZE_TYPE);

				cv::Mat grayFrame;
				cvtColor(patch, grayFrame, cv::COLOR_BGR2GRAY);
				grayFrame.convertTo(grayFrame, CV_TYPE);
				grayFrame = grayFrame / 255.0 - 0.5;
				features->channels[DFC::numberOfChannels() - 1] = grayFrame;
			}

			DFC::mulFeatures(features, _cosWindow);
			return true;
		}

		bool update_(const cv::Mat& image, Rect& boundingBox)
		{
			return updateAtScalePos(image, _pos, _scale, boundingBox);
		}

		bool updateAt_(const cv::Mat& image, Rect& boundingBox)
		{
			bool isValid = false;
			T scale = 0;
			Point pos(boundingBox.x + boundingBox.width * consts::c0_5,
				boundingBox.y + boundingBox.height * consts::c0_5);

			// caller's box may have a different aspect ratio
			// compared to the _targetSize; use the larger side
			// to calculate scale
			if (boundingBox.width > boundingBox.height)
				scale = boundingBox.width / _baseTargetSz.width;
			else
				scale = boundingBox.height / _baseTargetSz.height;

			isValid = updateAtScalePos(image, pos, scale, boundingBox);
			return isValid;
		}

		bool updateAtScalePos(const cv::Mat& image, const Point& oldPos, const T oldScale,
			Rect& boundingBox)
		{
			++_frameIdx;

			if (!_isInitialized)
				return false;

			T newScale = oldScale;
			Point newPos = oldPos;
			cv::Point2i maxResponseIdx;
			cv::Mat response;

			// in case of error return the last box
			boundingBox = _lastBoundingBox;

			if (detectModel(image, response, maxResponseIdx, newPos, newScale) == false)
				return false;

			// return box
			Rect tempBoundingBox;
			tempBoundingBox.width = _baseTargetSz.width * newScale;
			tempBoundingBox.height = _baseTargetSz.height * newScale;
			tempBoundingBox.x = newPos.x - tempBoundingBox.width / 2;
			tempBoundingBox.y = newPos.y - tempBoundingBox.height / 2;

			if (_ENABLE_TRACKING_LOSS_DETECTION)
			{
				if (evalReponse(image, response, maxResponseIdx,
					tempBoundingBox) == false)
					return false;
			}

			if (updateModel(image, newPos, newScale) == false)
				return false;

			boundingBox &= Rect(0, 0, static_cast<T>(image.cols), static_cast<T>(image.rows));
			boundingBox = tempBoundingBox;
			_lastBoundingBox = tempBoundingBox;
			return true;
		}

		bool evalReponse(const cv::Mat &image, const cv::Mat& response,
			const cv::Point2i& maxResponseIdx,
			const Rect& tempBoundingBox) const
		{
			T peakValue = 0;
			T psrClamped = calcPsr(response, maxResponseIdx, _PSR_PEAK_DEL, peakValue);

			if (psrClamped < _PSR_THRESHOLD)
				return false;

			// check if we are out of image, too small or too large
			Rect imageRect(Point(0, 0), image.size());
			Rect intersection = imageRect & tempBoundingBox;
			double  bbArea = tempBoundingBox.area();
			double areaThreshold = _MAX_AREA_FACTOR * imageRect.area();
			double intersectDiff = std::abs(bbArea - intersection.area());

			if (intersectDiff > 0.01 || bbArea < _MIN_AREA
				|| bbArea > areaThreshold)
				return false;

			return true;
		}

		bool detectModel(const cv::Mat& image, cv::Mat& response,
			cv::Point2i& maxResponseIdx, Point& newPos,
			T& newScale) const
		{
			// find translation
			std::shared_ptr<DFC> xt(0);

			if (getTranslationFeatures(image, xt, newPos, newScale) == false)
				return false;

			std::shared_ptr<DFC> xtf;
			if (_USE_CCS)
				xtf = DFC::dftFeatures(xt);
			else
				xtf = DFC::dftFeatures(xt, cv::DFT_COMPLEX_OUTPUT);

			std::shared_ptr<DFC> sampleSpec = DFC::mulSpectrumsFeatures(_hfNumerator, xtf, false);
			cv::Mat sumXtf = DFC::sumFeatures(sampleSpec);
			cv::Mat hfDenLambda = addRealToSpectrum<T>(_LAMBDA, _hfDenominator);
			cv::Mat responseTf;

			if (_USE_CCS)
				divSpectrums(sumXtf, hfDenLambda, responseTf, 0, false);
			else
				divideSpectrumsNoCcs<T>(sumXtf, hfDenLambda, responseTf);

			cv::Mat translationResponse;
			idft(responseTf, translationResponse, cv::DFT_REAL_OUTPUT | cv::DFT_SCALE);

			cv::Point delta;
			double maxResponse;
			cv::Point_<T> subDelta;
			minMaxLoc(translationResponse, 0, &maxResponse, 0, &delta);
			subDelta = delta;

			if (_CELL_SIZE != 1)
				subDelta = subPixelDelta<T>(translationResponse, delta);

			T posDeltaX = (subDelta.x + 1 - floor(translationResponse.cols / consts::c2_0)) * newScale;
			T posDeltaY = (subDelta.y + 1 - floor(translationResponse.rows / consts::c2_0)) * newScale;
			newPos.x += round(posDeltaX * _CELL_SIZE);
			newPos.y += round(posDeltaY * _CELL_SIZE);

			if (_scaleEstimator)
			{
				//find scale
				T tempScale = newScale * _templateScaleFactor;

				if (_scaleEstimator->detectScale(image, newPos,
					tempScale) == false)
					return false;

				newScale = tempScale / _templateScaleFactor;
			}

			response = translationResponse;
			maxResponseIdx = delta;
			return true;
		}

		bool updateModel(const cv::Mat& image, const Point& newPos,
			T newScale)
		{
			_pos = newPos;
			_scale = newScale;
			std::shared_ptr<DFC> hfNum(0);
			cv::Mat hfDen;

			if (getTranslationTrainingData(image, hfNum, hfDen, _pos) == false)
				return false;

			_hfDenominator = (1 - _LEARNING_RATE) * _hfDenominator + _LEARNING_RATE * hfDen;
			DFC::mulValueFeatures(_hfNumerator, (1 - _LEARNING_RATE));
			DFC::mulValueFeatures(hfNum, _LEARNING_RATE);
			DFC::addFeatures(_hfNumerator, hfNum);

			if (_scaleEstimator)
			{
				if (_scaleEstimator->updateScale(image, newPos, newScale * _templateScaleFactor) == false)
					return false;
			}

			return true;
		}

	private:
		typedef void(*cvFhogPtr)
			(const cv::Mat& img, std::shared_ptr<DFC>& cvFeatures, int binSize, int fhogChannelsToCopy);
		cvFhogPtr cvFhog = 0;

		typedef void(*dftPtr)
			(const cv::Mat& input, cv::Mat& output, int flags);
		dftPtr calcDft = 0;

		cv::Mat _cosWindow;
		cv::Mat _y;
		std::shared_ptr<DFC> _hfNumerator;
		cv::Mat _hfDenominator;
		cv::Mat _yf;
		Point _pos;
		Size _templateSz;
		Size _templateSizeNoFloor;
		Size _baseTargetSz;
		Rect _lastBoundingBox;
		T _scale; // _scale is the scale of the template; not the target
		T _templateScaleFactor; // _templateScaleFactor is used to calc the target scale
		ScaleEstimator<T>* _scaleEstimator;
		int _frameIdx = 1;
		bool _isInitialized;

		const T _MIN_AREA;
		const T _MAX_AREA_FACTOR;
		const T _PADDING;
		const T _OUTPUT_SIGMA_FACTOR;
		const T _LAMBDA;
		const T _LEARNING_RATE;
		const T _PSR_THRESHOLD;
		const int _PSR_PEAK_DEL;
		const int _CELL_SIZE;
		const int _TEMPLATE_SIZE;
		const bool _ENABLE_TRACKING_LOSS_DETECTION;
		const int _RESIZE_TYPE;
		const bool _ORIGINAL_VERSION;
		const bool _USE_CCS;

		T position[4];
	};
}

#endif