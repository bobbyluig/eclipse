#include <boost/python.hpp>
#include "kcf_export.h"
#include "kcf_tracker.hpp"

using namespace cf_tracking;
using namespace boost::python;

void KCF_EXPORT()
{
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
		.def_readwrite("votMinScaleFactor", &KcfParameters::VotMinScaleFactor)
		.def_readwrite("votMaxScaleFactor", &KcfParameters::VotMaxScaleFactor)
		.def_readwrite("useCcs", &KcfParameters::useCcs);

	class_<KcfTracker>("KcfTracker", init<KcfParameters>())
		.def("getBoundingBox", &KcfTracker::getBoundingBox)
		.def("getCenter", &KcfTracker::getCenter)
		.def("reinit", &KcfTracker::reinit)
		.def("update", &KcfTracker::update)
		.def("updateAt", &KcfTracker::updateAt);
}