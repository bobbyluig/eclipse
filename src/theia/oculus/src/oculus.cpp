#define PY_ARRAY_UNIQUE_SYMBOL pbcvt_ARRAY_API

#include <Python.h>
#include <boost/python/args.hpp>
#include <boost/python.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/module.hpp>
#include <pyboostcvconverter/pyboostcvconverter.hpp>

#include "kcf_export.h"
#include "dsst_export.h"
#include "line2d_export.h"

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
	PyEval_InitThreads();
	to_python_converter<cv::Mat,
	pbcvt::matToNDArrayBoostConverter>();
	pbcvt::matFromNDArrayBoostConverter();

	KCF_EXPORT();
	DSST_EXPORT();
	LINE2D_EXPORT();
}