#include <boost/python.hpp>
#include "saliency_export.h"
#include "saliency.hpp"

using namespace saliency;

void SALIENCY_EXPORT()
{
	class_<Saliency>("Saliency", init<int, int>())
		.def("compute", &Saliency::compute);
}