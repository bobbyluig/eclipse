#include <boost/python.hpp>
#include "line2d_export.h"
#include "line2d.hpp"
#include "linemod.hpp"
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

using namespace template_match;

typedef vector<cv::linemod::Match> Matches;

void LINE2D_EXPORT()
{
	class_<cv::linemod::Match>("Match")
		.def_readonly("x", &cv::linemod::Match::x)
		.def_readonly("y", &cv::linemod::Match::y)
		.def_readonly("similarity", &cv::linemod::Match::similarity)
		.def_readonly("class_id", &cv::linemod::Match::class_id)
		.def_readonly("template_id", &cv::linemod::Match::template_id);

	class_<Matches>("vector<Match>")
		.def(vector_indexing_suite<Matches>());

	class_<vector<int>>("vector<int>")
		.def(vector_indexing_suite<vector<int>>());

	class_<Line2DParameters>("Line2DParameters")
		.def_readwrite("weakThreshold", &Line2DParameters::weakThreshold)
		.def_readwrite("numFeatures", &Line2DParameters::numFeatures)
		.def_readwrite("strongThreshold", &Line2DParameters::strongThreshold)
		.def_readwrite("pyramid", &Line2DParameters::pyramid);

	class_<Line2D>("Line2D", init<Line2DParameters>())
		.def("addTemplate", &Line2D::addTemplate)
		.def("removeTemplate", &Line2D::removeTemplate)
		.def("removeClass", &Line2D::removeClass)
		.def("match", &Line2D::match)
		.def_readonly("numTemplates", &Line2D::numTemplates)
		.def_readonly("numTemplatesInClass", &Line2D::numTemplatesInClass)
		.def_readonly("numClasses", &Line2D::numClasses);
}