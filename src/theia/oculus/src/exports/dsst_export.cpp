#include <boost/python.hpp>
#include "dsst_export.h"
#include "dsst_tracker.hpp"

using namespace cf_tracking;
using namespace boost::python;

void DSST_EXPORT()
{
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