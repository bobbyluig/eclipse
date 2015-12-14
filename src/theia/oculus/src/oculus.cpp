#define PY_ARRAY_UNIQUE_SYMBOL pbcvt_ARRAY_API

#include <boost/python/args.hpp>
#include <boost/python.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/module.hpp>
#include <pyboostcvconverter/pyboostcvconverter.hpp>

#include <dsst_tracker.hpp>
#include <kcf_tracker.hpp>

using namespace cf_tracking;
using namespace boost::python;

static void* init_ar()
{
	Py_Initialize();
	import_array();

	return NULL;
}

BOOST_PYTHON_MODULE(oculus)
{
	init_ar();
	to_python_converter<cv::Mat,
	pbcvt::matToNDArrayBoostConverter>();
	pbcvt::matFromNDArrayBoostConverter();

	class_<KcfParameters>("KcfParameters")
		.def_readwrite("padding", &KcfParameters::padding)
		.def_readwrite("lambdaValue", &KcfParameters::lambda)
		.def_readwrite("outputSigmaFactor", &KcfParameters::outputSigmaFactor)
		.def_readwrite("votScaleStep", &KcfParameters::votScaleStep)
		.def_readwrite("votScaleWeight", &KcfParameters::votScaleWeight)
		.def_readwrite("templateSize", &KcfParameters::templateSize)
		.def_readwrite("interpFactor", &KcfParameters::interpFactor)
		.def_readwrite("kernelSigma", &KcfParameters::kernelSigma)
		.def_readwrite("cellSize", &KcfParameters::cellSize)
		.def_readwrite("pixelPadding", &KcfParameters::pixelPadding)
		.def_readwrite("enableTrackingLossDetection", &KcfParameters::enableTrackingLossDetection)
		.def_readwrite("psrThreshold", &KcfParameters::psrThreshold)
		.def_readwrite("psrPeakDel", &KcfParameters::psrPeakDel)
		.def_readwrite("useVotScaleEstimation", &KcfParameters::useVotScaleEstimation)
		.def_readwrite("useDsstScaleEstimation", &KcfParameters::useDsstScaleEstimation)
		.def_readwrite("scaleSigmaFactor", &KcfParameters::scaleSigmaFactor)
		.def_readwrite("scaleEstimatorStep", &KcfParameters::scaleEstimatorStep)
		.def_readwrite("scaleLambda", &KcfParameters::scaleLambda)
		.def_readwrite("numberOfScales", &KcfParameters::numberOfScales)
		.def_readwrite("resizeType", &KcfParameters::resizeType)
		.def_readwrite("useFhogTranspose", &KcfParameters::useFhogTranspose)
		.def_readwrite("minArea", &KcfParameters::minArea)
		.def_readwrite("maxAreaFactor", &KcfParameters::maxAreaFactor)
		.def_readwrite("nScalesVot", &KcfParameters::nScalesVot)
		.def_readwrite("VotMinScaleFactor", &KcfParameters::VotMinScaleFactor)
		.def_readwrite("VotMaxScaleFactor", &KcfParameters::VotMaxScaleFactor)
		.def_readwrite("useCcs", &KcfParameters::useCcs);

	class_<KcfTracker>("KcfTracker", init<KcfParameters>())
		.def("getBoundingBox", &KcfTracker::getBoundingBox)
		.def("getCenter", &KcfTracker::getCenter)
		.def("reinit", &KcfTracker::reinit)
		.def("update", &KcfTracker::update)
		.def("updateAt", &KcfTracker::updateAt);

	class_<DsstParameters>("DsstParameters")
		.def_readwrite("padding", &DsstParameters::padding)
		.def_readwrite("outputSigmaFactor", &DsstParameters::outputSigmaFactor)
		.def_readwrite("lambdaValue", &DsstParameters::lambda)
		.def_readwrite("learningRate", &DsstParameters::learningRate)
		.def_readwrite("templateSize", &DsstParameters::templateSize)
		.def_readwrite("cellSize", &DsstParameters::cellSize)
		.def_readwrite("enableTrackingLossDetection", &DsstParameters::enableTrackingLossDetection)
		.def_readwrite("psrThreshold", &DsstParameters::psrThreshold)
		.def_readwrite("psrPeakDel", &DsstParameters::psrPeakDel)
		.def_readwrite("enableScaleEstimator", &DsstParameters::enableScaleEstimator)
		.def_readwrite("scaleSigmaFactor", &DsstParameters::scaleSigmaFactor)
		.def_readwrite("scaleStep", &DsstParameters::scaleStep)
		.def_readwrite("scaleCellSize", &DsstParameters::scaleCellSize)
		.def_readwrite("numberOfScales", &DsstParameters::numberOfScales)
		.def_readwrite("originalVersion", &DsstParameters::originalVersion)
		.def_readwrite("resizeType", &DsstParameters::resizeType)
		.def_readwrite("useFhogTranspose", &DsstParameters::useFhogTranspose)
		.def_readwrite("minArea", &DsstParameters::minArea)
		.def_readwrite("maxAreaFactor", &DsstParameters::maxAreaFactor)
		.def_readwrite("useCcs", &DsstParameters::useCcs);

	class_<DsstTracker>("DsstTracker", init<DsstParameters>())
		.def("getBoundingBox", &DsstTracker::getBoundingBox)
		.def("getCenter", &DsstTracker::getCenter)
		.def("reinit", &DsstTracker::reinit)
		.def("update", &DsstTracker::update)
		.def("updateAt", &DsstTracker::updateAt);
}