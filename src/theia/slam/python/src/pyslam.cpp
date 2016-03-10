#define PY_ARRAY_UNIQUE_SYMBOL pbcvt_ARRAY_API

#include <Python.h>
#include <boost/python.hpp>
#include <pyboostcvconverter/pyboostcvconverter.hpp>

#include <Tracking.h>
#include <System.h>
#include <ORBVocabulary.h>
#include <Map.h>
#include <LocalMapping.h>
#include <LoopClosing.h>
#include <KeyFrameDatabase.h>

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

	class_<Tracking, boost::noncopyable>("Tracking", 
		init<ORBVocabulary&, Map&, KeyFrameDatabase&, TrackerParams&, int>())
		.def("set_loop_closer", &Tracking::SetLoopCloser)
		.def("set_local_mapper", &Tracking::SetLocalMapper)
		.def("run", &Tracking::Run)
		.def("grab_one", &Tracking::GrabImageMonocular)
		.def("get_state", &Tracking::GetState);

	// MEMORY LEAK!!!
	class_<ORBVocabulary>("ORBVocabulary")
		.def("load", &ORBVocabulary::loadFromTextFile)
		.def("load2", &ORBVocabulary::loadFromTextFile2);

	class_<KeyFrameDatabase, boost::noncopyable>("KeyFrameDatabase", 
		init<ORBVocabulary&>())
		.def("clear", &KeyFrameDatabase::clear);

	class_<Map, boost::noncopyable>("Map")
		.def("clear", &Map::clear);

	class_<LocalMapping, boost::noncopyable>("LocalMapping", 
		init<Map&, bool>())
		.def("run", &LocalMapping::Run)
		.def("finish", &LocalMapping::RequestFinish)
		.def("reset", &LocalMapping::RequestReset)
		.def("set_loop_closer", &LocalMapping::SetLoopCloser);

	class_<LoopClosing, boost::noncopyable>("LoopClosing", 
		init<Map&, KeyFrameDatabase&, ORBVocabulary&, bool>())
		.def("run", &LoopClosing::Run)
		.def("finish", &LoopClosing::RequestFinish)
		.def("reset", &LoopClosing::RequestReset)
		.def("set_local_mapper", &LoopClosing::SetLocalMapper);

	enum_<System::eSensor>("eSensor")
		.value("MONOCULAR", System::MONOCULAR)
		.value("STEREO", System::STEREO)
		.value("RGBD", System::RGBD);
}

BOOST_PYTHON_MODULE(pyslam)
{
	init_ar();
	PyEval_InitThreads();
	to_python_converter<cv::Mat, pbcvt::matToNDArrayBoostConverter>();
	pbcvt::matFromNDArrayBoostConverter();

	export_all();
}