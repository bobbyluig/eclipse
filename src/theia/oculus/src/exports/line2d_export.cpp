#include <boost/python.hpp>
#include "line2d_export.h"
#include "line2d.hpp"
#include "linemod.hpp"
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

using namespace template_match;

typedef vector<cv::linemod::Match> Matches;

/// @brief Type that allows for registration of conversions from
///        python iterable types.
struct iterable_converter
{
	/// @note Registers converter from a python interable type to the
	///       provided type.
	template <typename Container>
	iterable_converter&
		from_python()
	{
		boost::python::converter::registry::push_back(
			&iterable_converter::convertible,
			&iterable_converter::construct<Container>,
			boost::python::type_id<Container>());

		// Support chaining.
		return *this;
	}

	/// @brief Check if PyObject is iterable.
	static void* convertible(PyObject* object)
	{
		return PyObject_GetIter(object) ? object : NULL;
	}

	/// @brief Convert iterable PyObject to C++ container type.
	///
	/// Container Concept requirements:
	///
	///   * Container::value_type is CopyConstructable.
	///   * Container can be constructed and populated with two iterators.
	///     I.e. Container(begin, end)
	template <typename Container>
	static void construct(
		PyObject* object,
		boost::python::converter::rvalue_from_python_stage1_data* data)
	{
		namespace python = boost::python;
		// Object is a borrowed reference, so create a handle indicting it is
		// borrowed for proper reference counting.
		python::handle<> handle(python::borrowed(object));

		// Obtain a handle to the memory block that the converter has allocated
		// for the C++ type.
		typedef python::converter::rvalue_from_python_storage<Container>
			storage_type;
		void* storage = reinterpret_cast<storage_type*>(data)->storage.bytes;

		typedef python::stl_input_iterator<typename Container::value_type>
			iterator;

		// Allocate the C++ type into the converter's memory block, and assign
		// its handle to the converter's convertible variable.  The C++
		// container is populated by passing the begin and end iterators of
		// the python object to the container's constructor.
		new (storage) Container(
			iterator(python::object(handle)), // begin
			iterator());                      // end
		data->convertible = storage;
	}
};

void LINE2D_EXPORT()
{
	// Output vector registration
	class_<Matches>("vector<Match>")
		.def(vector_indexing_suite<Matches>());

	class_<vector<int>>("vector<int>")
		.def(vector_indexing_suite<vector<int>>());

	// Input vector registration
	iterable_converter()
		.from_python<vector<int>>();

	// Class registration
	class_<cv::linemod::Match>("Match")
		.def_readonly("x", &cv::linemod::Match::x)
		.def_readonly("y", &cv::linemod::Match::y)
		.def_readonly("width", &cv::linemod::Match::width)
		.def_readonly("height", &cv::linemod::Match::height)
		.def_readonly("similarity", &cv::linemod::Match::similarity)
		.def_readonly("class_id", &cv::linemod::Match::class_id)
		.def_readonly("template_id", &cv::linemod::Match::template_id);

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
		.def("exportTemplate", &Line2D::exportTemplate)
		.def("importTemplate", &Line2D::importTemplate)
		.def("exportClass", &Line2D::exportClass)
		.def("importClass", &Line2D::importClass)
		.def_readonly("numTemplates", &Line2D::numTemplates)
		.def("numTemplatesInClass", &Line2D::numTemplatesInClass)
		.def_readonly("numClasses", &Line2D::numClasses);
}