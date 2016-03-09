#define PY_ARRAY_UNIQUE_SYMBOL pbcvt_ARRAY_API

#include <Python.h>
#include <boost/python.hpp>
#include <pyboostcvconverter/pyboostcvconverter.hpp>

#include <Tracking.h>
#include <System.h>

using namespace boost::python;
using namespace ORB_SLAM2;

static void* init_ar()
{
	Py_Initialize();
	import_array();

	return NULL;
}

void export_all()
{
	class_<TrackerParams>("TrackerParams")
		.def_readwrite("fx", &TrackerParams::fx)
		.def_readwrite("fy", &TrackerParams::fy)
		.def_readwrite("cx", &TrackerParams::cx)
		.def_readwrite("cy", &TrackerParams::cy)
		.def_readwrite("k1", &TrackerParams::k1)
		.def_readwrite("k2", &TrackerParams::k2)
		.def_readwrite("k3", &TrackerParams::k3)
		.def_readwrite("p1", &TrackerParams::p1)
		.def_readwrite("p2", &TrackerParams::p2)
		.def_readwrite("bf", &TrackerParams::bf)
		.def_readwrite("fps", &TrackerParams::fps)
		.def_readwrite("rgb", &TrackerParams::RGB)
		.def_readwrite("nFeatures", &TrackerParams::nFeatures)
		.def_readwrite("fScaleFactor", &TrackerParams::fScaleFactor)
		.def_readwrite("nLevels", &TrackerParams::nLevels)
		.def_readwrite("fIniThFAST", &TrackerParams::fIniThFAST)
		.def_readwrite("fMinThFAST", &TrackerParams::fMinThFAST)
		.def_readwrite("mThDepth", &TrackerParams::mThDepth)
		.def_readwrite("mDepthMapFactor", &TrackerParams::mDepthMapFactor);

	class_<Tracking, boost::noncopyable>("Tracking", init<TrackerParams&, int>())
		.def("run", &Tracking::Run)
		.def("grab_one", &Tracking::GrabImageMonocular)
		.def("get_state", &Tracking::GetState);

	class_<System>("System")
		.def("load", &System::Load)
		.def("start", &System::Start)
		.def("stop", &System::Stop)
		.def("bind_tracker", &System::BindTracker);
}

BOOST_PYTHON_MODULE(pyslam)
{
	init_ar();
	PyEval_InitThreads();
	to_python_converter<cv::Mat, pbcvt::matToNDArrayBoostConverter>();
	pbcvt::matFromNDArrayBoostConverter();

	export_all();
}