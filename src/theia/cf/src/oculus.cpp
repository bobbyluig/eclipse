#define PY_ARRAY_UNIQUE_SYMBOL pbcvt_ARRAY_API

#include <boost/python/args.hpp>
#include <boost/python.hpp>
#include <boost/python/tuple.hpp>
#include <pyboostcvconverter/pyboostcvconverter.hpp>

#include <dsst_tracker.hpp>

using namespace cf_tracking;
using namespace boost::python;

static void* init_ar()
{
	Py_Initialize();
	import_array();

	return NULL;
}

BOOST_PYTHON_MODULE(tracker)
{
	init_ar();
	to_python_converter<cv::Mat,
	pbcvt::matToNDArrayBoostConverter>();
	pbcvt::matFromNDArrayBoostConverter();

	class_<DsstParameters>("DsstParameters")
		.def_readwrite("padding", &DsstParameters::padding)
		.def_readwrite("outputSigmaFactor", &DsstParameters::outputSigmaFactor)
		.def_readwrite("lambda", &DsstParameters::lambda)
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
		.def_readwrite("useFhogTranspose", &DsstParameters::useFhogTranspose);

	class_<DsstTracker>("DsstTracker", init<DsstParameters>())
		.def("getPosition", &DsstTracker::getPosition)
		.def("reinit", &DsstTracker::reinit)
		.def("update", &DsstTracker::update)
		.def("update", &DsstTracker::updateAt);
}