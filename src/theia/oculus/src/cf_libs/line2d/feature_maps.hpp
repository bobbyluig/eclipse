#ifndef LINE2D_FEATURE_MAPS_H_
#define LINE2D_FEATURE_MAPS_H_

#include <opencv2/core/core.hpp>

namespace template_matching
{
	template<int nOrients>
	class FeatureMaps
	{
	public:
		cv::Mat maps[nOrients];
	};
}

#endif