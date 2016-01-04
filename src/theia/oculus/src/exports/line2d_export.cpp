#include <boost/python.hpp>
#include "line2d_export.h"
#include "line2d.hpp"

using namespace template_match;

void LINE2D_EXPORT()
{
	class_<Line2DParameters>("Line2DParameters")
		.def_readwrite("numQuantizations", &Line2DParameters::numQuantizations)
		.def_readwrite("threshold", &Line2DParameters::threshold)
		.def_readwrite("useGaussian", &Line2DParameters::useGaussian)
		.def_readwrite("tau", &Line2DParameters::tau);

	class_<Line2D>("Line2D", init<Line2DParameters>())
		.def("test", &Line2D::test)
		.def("test2", &Line2D::test2);
}