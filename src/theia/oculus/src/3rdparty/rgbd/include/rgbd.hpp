/*
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2009, Willow Garage, Inc.
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of Willow Garage, Inc. nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *
 */

#ifndef __OPENCV_RGBD_HPP__
#define __OPENCV_RGBD_HPP__

#ifdef __cplusplus

#include <opencv2/core.hpp>
#include <limits>

/** @defgroup rgbd RGB-Depth Processing
*/

namespace cv
{
namespace rgbd
{

//! @addtogroup rgbd
//! @{

  /** Checks if the value is a valid depth. For CV_16U or CV_16S, the convention is to be invalid if it is
   * a limit. For a float/double, we just check if it is a NaN
   * @param depth the depth to check for validity
   */
  CV_EXPORTS
  inline bool
  isValidDepth(const float & depth)
  {
    return !cvIsNaN(depth);
  }
  CV_EXPORTS
  inline bool
  isValidDepth(const double & depth)
  {
    return !cvIsNaN(depth);
  }
  CV_EXPORTS
  inline bool
  isValidDepth(const short int & depth)
  {
    return (depth != std::numeric_limits<short int>::min()) && (depth != std::numeric_limits<short int>::max());
  }
  CV_EXPORTS
  inline bool
  isValidDepth(const unsigned short int & depth)
  {
    return (depth != std::numeric_limits<unsigned short int>::min())
        && (depth != std::numeric_limits<unsigned short int>::max());
  }
  CV_EXPORTS
  inline bool
  isValidDepth(const int & depth)
  {
    return (depth != std::numeric_limits<int>::min()) && (depth != std::numeric_limits<int>::max());
  }
  CV_EXPORTS
  inline bool
  isValidDepth(const unsigned int & depth)
  {
    return (depth != std::numeric_limits<unsigned int>::min()) && (depth != std::numeric_limits<unsigned int>::max());
  }

  /** Object that can compute the normals in an image.
   * It is an object as it can cache data for speed efficiency
   * The implemented methods are either:
   * - FALS (the fastest) and SRI from
   * ``Fast and Accurate Computation of Surface Normals from Range Images``
   * by H. Badino, D. Huber, Y. Park and T. Kanade
   * - the normals with bilateral filtering on a depth image from
   * ``Gradient Response Maps for Real-Time Detection of Texture-Less Objects``
   * by S. Hinterstoisser, C. Cagniart, S. Ilic, P. Sturm, N. Navab, P. Fua, and V. Lepetit
   */
  class CV_EXPORTS RgbdNormals: public Algorithm
  {
  public:
    enum RGBD_NORMALS_METHOD
    {
      RGBD_NORMALS_METHOD_FALS, RGBD_NORMALS_METHOD_LINEMOD, RGBD_NORMALS_METHOD_SRI
    };

    RgbdNormals()
        :
          rows_(0),
          cols_(0),
          depth_(0),
          K_(Mat()),
          window_size_(0),
          method_(RGBD_NORMALS_METHOD_FALS),
          rgbd_normals_impl_(0)
    {
    }

    /** Constructor
     * @param rows the number of rows of the depth image normals will be computed on
     * @param cols the number of cols of the depth image normals will be computed on
     * @param depth the depth of the normals (only CV_32F or CV_64F)
     * @param K the calibration matrix to use
     * @param window_size the window size to compute the normals: can only be 1,3,5 or 7
     * @param method one of the methods to use: RGBD_NORMALS_METHOD_SRI, RGBD_NORMALS_METHOD_FALS
     */
    RgbdNormals(int rows, int cols, int depth, InputArray K, int window_size = 5, int method =
        RGBD_NORMALS_METHOD_FALS);

    ~RgbdNormals();

    /** Given a set of 3d points in a depth image, compute the normals at each point.
     * @param points a rows x cols x 3 matrix of CV_32F/CV64F or a rows x cols x 1 CV_U16S
     * @param normals a rows x cols x 3 matrix
     */
    void
    operator()(InputArray points, OutputArray normals) const;

    /** Initializes some data that is cached for later computation
     * If that function is not called, it will be called the first time normals are computed
     */
    void
    initialize() const;

    int getRows() const
    {
        return rows_;
    }
    void setRows(int val)
    {
        rows_ = val;
    }
    int getCols() const
    {
        return cols_;
    }
    void setCols(int val)
    {
        cols_ = val;
    }
    int getWindowSize() const
    {
        return window_size_;
    }
    void setWindowSize(int val)
    {
        window_size_ = val;
    }
    int getDepth() const
    {
        return depth_;
    }
    void setDepth(int val)
    {
        depth_ = val;
    }
    cv::Mat getK() const
    {
        return K_;
    }
    void setK(const cv::Mat &val)
    {
        K_ = val;
    }
    int getMethod() const
    {
        return method_;
    }
    void setMethod(int val)
    {
        method_ = val;
    }

  protected:
    void
    initialize_normals_impl(int rows, int cols, int depth, const Mat & K, int window_size, int method) const;

    int rows_, cols_, depth_;
    Mat K_;
    int window_size_;
    int method_;
    mutable void* rgbd_normals_impl_;
  };

  /** Object that can clean a noisy depth image
   */
  class CV_EXPORTS DepthCleaner: public Algorithm
  {
  public:
    /** NIL method is from
     * ``Modeling Kinect Sensor Noise for Improved 3d Reconstruction and Tracking``
     * by C. Nguyen, S. Izadi, D. Lovel
     */
    enum DEPTH_CLEANER_METHOD
    {
      DEPTH_CLEANER_NIL
    };

    DepthCleaner()
        :
          depth_(0),
          window_size_(0),
          method_(DEPTH_CLEANER_NIL),
          depth_cleaner_impl_(0)
    {
    }

    /** Constructor
     * @param depth the depth of the normals (only CV_32F or CV_64F)
     * @param window_size the window size to compute the normals: can only be 1,3,5 or 7
     * @param method one of the methods to use: RGBD_NORMALS_METHOD_SRI, RGBD_NORMALS_METHOD_FALS
     */
    DepthCleaner(int depth, int window_size = 5, int method = DEPTH_CLEANER_NIL);

    ~DepthCleaner();

    /** Given a set of 3d points in a depth image, compute the normals at each point.
     * @param points a rows x cols x 3 matrix of CV_32F/CV64F or a rows x cols x 1 CV_U16S
     * @param depth a rows x cols matrix of the cleaned up depth
     */
    void
    operator()(InputArray points, OutputArray depth) const;

    /** Initializes some data that is cached for later computation
     * If that function is not called, it will be called the first time normals are computed
     */
    void
    initialize() const;

    int getWindowSize() const
    {
        return window_size_;
    }
    void setWindowSize(int val)
    {
        window_size_ = val;
    }
    int getDepth() const
    {
        return depth_;
    }
    void setDepth(int val)
    {
        depth_ = val;
    }
    int getMethod() const
    {
        return method_;
    }
    void setMethod(int val)
    {
        method_ = val;
    }

  protected:
    void
    initialize_cleaner_impl() const;

    int depth_;
    int window_size_;
    int method_;
    mutable void* depth_cleaner_impl_;
  };


  /** Registers depth data to an external camera
   * Registration is performed by creating a depth cloud, transforming the cloud by
   * the rigid body transformation between the cameras, and then projecting the
   * transformed points into the RGB camera.
   *
   * uv_rgb = K_rgb * [R | t] * z * inv(K_ir) * uv_ir
   *
   * Currently does not check for negative depth values.
   *
   * @param unregisteredCameraMatrix the camera matrix of the depth camera
   * @param registeredCameraMatrix the camera matrix of the external camera
   * @param registeredDistCoeffs the distortion coefficients of the external camera
   * @param Rt the rigid body transform between the cameras. Transforms points from depth camera frame to external camera frame.
   * @param unregisteredDepth the input depth data
   * @param outputImagePlaneSize the image plane dimensions of the external camera (width, height)
   * @param registeredDepth the result of transforming the depth into the external camera
   * @param depthDilation whether or not the depth is dilated to avoid holes and occlusion errors (optional)
   */
  CV_EXPORTS
  void
  registerDepth(InputArray unregisteredCameraMatrix, InputArray registeredCameraMatrix, InputArray registeredDistCoeffs,
                InputArray Rt, InputArray unregisteredDepth, const Size& outputImagePlaneSize,
                OutputArray registeredDepth, bool depthDilation=false);

  /**
   * @param depth the depth image
   * @param in_K
   * @param in_points the list of xy coordinates
   * @param points3d the resulting 3d points
   */
  CV_EXPORTS
  void
  depthTo3dSparse(InputArray depth, InputArray in_K, InputArray in_points, OutputArray points3d);

  /** Converts a depth image to an organized set of 3d points.
   * The coordinate system is x pointing left, y down and z away from the camera
   * @param depth the depth image (if given as short int CV_U, it is assumed to be the depth in millimeters
   *              (as done with the Microsoft Kinect), otherwise, if given as CV_32F or CV_64F, it is assumed in meters)
   * @param K The calibration matrix
   * @param points3d the resulting 3d points. They are of depth the same as `depth` if it is CV_32F or CV_64F, and the
   *        depth of `K` if `depth` is of depth CV_U
   * @param mask the mask of the points to consider (can be empty)
   */
  CV_EXPORTS
  void
  depthTo3d(InputArray depth, InputArray K, OutputArray points3d, InputArray mask = noArray());

  /** If the input image is of type CV_16UC1 (like the Kinect one), the image is converted to floats, divided
   * by 1000 to get a depth in meters, and the values 0 are converted to std::numeric_limits<float>::quiet_NaN()
   * Otherwise, the image is simply converted to floats
   * @param in the depth image (if given as short int CV_U, it is assumed to be the depth in millimeters
   *              (as done with the Microsoft Kinect), it is assumed in meters)
   * @param depth the desired output depth (floats or double)
   * @param out The rescaled float depth image
   */
  CV_EXPORTS
  void
  rescaleDepth(InputArray in, int depth, OutputArray out);

  /** Object that can compute planes in an image
   */
  class CV_EXPORTS RgbdPlane: public Algorithm
  {
  public:
    enum RGBD_PLANE_METHOD
    {
      RGBD_PLANE_METHOD_DEFAULT
    };

    RgbdPlane(RGBD_PLANE_METHOD method = RGBD_PLANE_METHOD_DEFAULT)
        :
          method_(method),
          block_size_(40),
          min_size_(block_size_*block_size_),
          threshold_(0.01),
          sensor_error_a_(0),
          sensor_error_b_(0),
          sensor_error_c_(0)
    {
    }

    /** Find The planes in a depth image
     * @param points3d the 3d points organized like the depth image: rows x cols with 3 channels
     * @param normals the normals for every point in the depth image
     * @param mask An image where each pixel is labeled with the plane it belongs to
     *        and 255 if it does not belong to any plane
     * @param plane_coefficients the coefficients of the corresponding planes (a,b,c,d) such that ax+by+cz+d=0, norm(a,b,c)=1
     *        and c < 0 (so that the normal points towards the camera)
     */
    void
    operator()(InputArray points3d, InputArray normals, OutputArray mask,
               OutputArray plane_coefficients);

    /** Find The planes in a depth image but without doing a normal check, which is faster but less accurate
     * @param points3d the 3d points organized like the depth image: rows x cols with 3 channels
     * @param mask An image where each pixel is labeled with the plane it belongs to
     *        and 255 if it does not belong to any plane
     * @param plane_coefficients the coefficients of the corresponding planes (a,b,c,d) such that ax+by+cz+d=0
     */
    void
    operator()(InputArray points3d, OutputArray mask, OutputArray plane_coefficients);

    int getBlockSize() const
    {
        return block_size_;
    }
    void setBlockSize(int val)
    {
        block_size_ = val;
    }
    int getMinSize() const
    {
        return min_size_;
    }
    void setMinSize(int val)
    {
        min_size_ = val;
    }
    int getMethod() const
    {
        return method_;
    }
    void setMethod(int val)
    {
        method_ = val;
    }
    double getThreshold() const
    {
        return threshold_;
    }
    void setThreshold(double val)
    {
        threshold_ = val;
    }
    double getSensorErrorA() const
    {
        return sensor_error_a_;
    }
    void setSensorErrorA(double val)
    {
        sensor_error_a_ = val;
    }
    double getSensorErrorB() const
    {
        return sensor_error_b_;
    }
    void setSensorErrorB(double val)
    {
        sensor_error_b_ = val;
    }
    double getSensorErrorC() const
    {
        return sensor_error_c_;
    }
    void setSensorErrorC(double val)
    {
        sensor_error_c_ = val;
    }

  private:
    /** The method to use to compute the planes */
    int method_;
    /** The size of the blocks to look at for a stable MSE */
    int block_size_;
    /** The minimum size of a cluster to be considered a plane */
    int min_size_;
    /** How far a point can be from a plane to belong to it (in meters) */
    double threshold_;
    /** coefficient of the sensor error with respect to the. All 0 by default but you want a=0.0075 for a Kinect */
    double sensor_error_a_, sensor_error_b_, sensor_error_c_;
  };

  /** Object that contains a frame data.
   */
  struct CV_EXPORTS RgbdFrame
  {
      RgbdFrame();
      RgbdFrame(const Mat& image, const Mat& depth, const Mat& mask=Mat(), const Mat& normals=Mat(), int ID=-1);
      virtual ~RgbdFrame();

      virtual void
      release();

      int ID;
      Mat image;
      Mat depth;
      Mat mask;
      Mat normals;
  };

  /** Object that contains a frame data that is possibly needed for the Odometry.
   * It's used for the efficiency (to pass precomputed/cached data of the frame that participates
   * in the Odometry processing several times).
   */
  struct CV_EXPORTS OdometryFrame : public RgbdFrame
  {
    /** These constants are used to set a type of cache which has to be prepared depending on the frame role:
     * srcFrame or dstFrame (see compute method of the Odometry class). For the srcFrame and dstFrame different cache data may be required,
     * some part of a cache may be common for both frame roles.
     * @param CACHE_SRC The cache data for the srcFrame will be prepared.
     * @param CACHE_DST The cache data for the dstFrame will be prepared.
     * @param CACHE_ALL The cache data for both srcFrame and dstFrame roles will be computed.
     */
    enum
    {
      CACHE_SRC = 1, CACHE_DST = 2, CACHE_ALL = CACHE_SRC + CACHE_DST
    };

    OdometryFrame();
    OdometryFrame(const Mat& image, const Mat& depth, const Mat& mask=Mat(), const Mat& normals=Mat(), int ID=-1);

    virtual void
    release();

    void
    releasePyramids();

    std::vector<Mat> pyramidImage;
    std::vector<Mat> pyramidDepth;
    std::vector<Mat> pyramidMask;

    std::vector<Mat> pyramidCloud;

    std::vector<Mat> pyramid_dI_dx;
    std::vector<Mat> pyramid_dI_dy;
    std::vector<Mat> pyramidTexturedMask;

    std::vector<Mat> pyramidNormals;
    std::vector<Mat> pyramidNormalsMask;
  };

  /** Base class for computation of odometry.
   */
  class CV_EXPORTS Odometry: public Algorithm
  {
  public:

    /** A class of transformation*/
    enum
    {
      ROTATION = 1, TRANSLATION = 2, RIGID_BODY_MOTION = 4
    };

    static inline float
    DEFAULT_MIN_DEPTH()
    {
      return 0.f; // in meters
    }
    static inline float
    DEFAULT_MAX_DEPTH()
    {
      return 4.f; // in meters
    }
    static inline float
    DEFAULT_MAX_DEPTH_DIFF()
    {
      return 0.07f; // in meters
    }
    static inline float
    DEFAULT_MAX_POINTS_PART()
    {
      return 0.07f; // in [0, 1]
    }
    static inline float
    DEFAULT_MAX_TRANSLATION()
    {
      return 0.15f; // in meters
    }
    static inline float
    DEFAULT_MAX_ROTATION()
    {
      return 15; // in degrees
    }

    /** Method to compute a transformation from the source frame to the destination one.
     * Some odometry algorithms do not used some data of frames (eg. ICP does not use images).
     * In such case corresponding arguments can be set as empty Mat.
     * The method returns true if all internal computions were possible (e.g. there were enough correspondences,
     * system of equations has a solution, etc) and resulting transformation satisfies some test if it's provided
     * by the Odometry inheritor implementation (e.g. thresholds for maximum translation and rotation).
     * @param srcImage Image data of the source frame (CV_8UC1)
     * @param srcDepth Depth data of the source frame (CV_32FC1, in meters)
     * @param srcMask Mask that sets which pixels have to be used from the source frame (CV_8UC1)
     * @param dstImage Image data of the destination frame (CV_8UC1)
     * @param dstDepth Depth data of the destination frame (CV_32FC1, in meters)
     * @param dstMask Mask that sets which pixels have to be used from the destination frame (CV_8UC1)
     * @param Rt Resulting transformation from the source frame to the destination one (rigid body motion):
     dst_p = Rt * src_p, where dst_p is a homogeneous point in the destination frame and src_p is
     homogeneous point in the source frame,
     Rt is 4x4 matrix of CV_64FC1 type.
     * @param initRt Initial transformation from the source frame to the destination one (optional)
     */
    bool
    compute(const Mat& srcImage, const Mat& srcDepth, const Mat& srcMask, const Mat& dstImage, const Mat& dstDepth,
            const Mat& dstMask, Mat& Rt, const Mat& initRt = Mat()) const;

    /** One more method to compute a transformation from the source frame to the destination one.
     * It is designed to save on computing the frame data (image pyramids, normals, etc.).
     */
    bool
    compute(Ptr<OdometryFrame>& srcFrame, Ptr<OdometryFrame>& dstFrame, Mat& Rt, const Mat& initRt = Mat()) const;

    /** Prepare a cache for the frame. The function checks the precomputed/passed data (throws the error if this data
     * does not satisfy) and computes all remaining cache data needed for the frame. Returned size is a resolution
     * of the prepared frame.
     * @param frame The odometry which will process the frame.
     * @param cacheType The cache type: CACHE_SRC, CACHE_DST or CACHE_ALL.
     */
    virtual Size prepareFrameCache(Ptr<OdometryFrame>& frame, int cacheType) const;

    static Ptr<Odometry> create(const String & odometryType);

    /** @see setCameraMatrix */
    virtual cv::Mat getCameraMatrix() const = 0;
    /** @copybrief getCameraMatrix @see getCameraMatrix */
    virtual void setCameraMatrix(const cv::Mat &val) = 0;
    /** @see setTransformType */
    virtual int getTransformType() const = 0;
    /** @copybrief getTransformType @see getTransformType */
    virtual void setTransformType(int val) = 0;

  protected:
    virtual void
    checkParams() const = 0;

    virtual bool
    computeImpl(const Ptr<OdometryFrame>& srcFrame, const Ptr<OdometryFrame>& dstFrame, Mat& Rt,
                const Mat& initRt) const = 0;
  };

  /** Odometry based on the paper "Real-Time Visual Odometry from Dense RGB-D Images",
   * F. Steinbucker, J. Strum, D. Cremers, ICCV, 2011.
   */
  class CV_EXPORTS RgbdOdometry: public Odometry
  {
  public:
    RgbdOdometry();
    /** Constructor.
     * @param cameraMatrix Camera matrix
     * @param minDepth Pixels with depth less than minDepth will not be used (in meters)
     * @param maxDepth Pixels with depth larger than maxDepth will not be used (in meters)
     * @param maxDepthDiff Correspondences between pixels of two given frames will be filtered out
     *                     if their depth difference is larger than maxDepthDiff (in meters)
     * @param iterCounts Count of iterations on each pyramid level.
     * @param minGradientMagnitudes For each pyramid level the pixels will be filtered out
     *                              if they have gradient magnitude less than minGradientMagnitudes[level].
     * @param maxPointsPart The method uses a random pixels subset of size frameWidth x frameHeight x pointsPart
     * @param transformType Class of transformation
     */
    RgbdOdometry(const Mat& cameraMatrix, float minDepth = DEFAULT_MIN_DEPTH(), float maxDepth = DEFAULT_MAX_DEPTH(),
                 float maxDepthDiff = DEFAULT_MAX_DEPTH_DIFF(), const std::vector<int>& iterCounts = std::vector<int>(),
                 const std::vector<float>& minGradientMagnitudes = std::vector<float>(), float maxPointsPart = DEFAULT_MAX_POINTS_PART(),
                 int transformType = RIGID_BODY_MOTION);

    virtual Size prepareFrameCache(Ptr<OdometryFrame>& frame, int cacheType) const;

    cv::Mat getCameraMatrix() const
    {
        return cameraMatrix;
    }
    void setCameraMatrix(const cv::Mat &val)
    {
        cameraMatrix = val;
    }
    double getMinDepth() const
    {
        return minDepth;
    }
    void setMinDepth(double val)
    {
        minDepth = val;
    }
    double getMaxDepth() const
    {
        return maxDepth;
    }
    void setMaxDepth(double val)
    {
        maxDepth = val;
    }
    double getMaxDepthDiff() const
    {
        return maxDepthDiff;
    }
    void setMaxDepthDiff(double val)
    {
        maxDepthDiff = val;
    }
    cv::Mat getIterationCounts() const
    {
        return iterCounts;
    }
    void setIterationCounts(const cv::Mat &val)
    {
        iterCounts = val;
    }
    cv::Mat getMinGradientMagnitudes() const
    {
        return minGradientMagnitudes;
    }
    void setMinGradientMagnitudes(const cv::Mat &val)
    {
        minGradientMagnitudes = val;
    }
    double getMaxPointsPart() const
    {
        return maxPointsPart;
    }
    void setMaxPointsPart(double val)
    {
        maxPointsPart = val;
    }
    int getTransformType() const
    {
        return transformType;
    }
    void setTransformType(int val)
    {
        transformType = val;
    }
    double getMaxTranslation() const
    {
        return maxTranslation;
    }
    void setMaxTranslation(double val)
    {
        maxTranslation = val;
    }
    double getMaxRotation() const
    {
        return maxRotation;
    }
    void setMaxRotation(double val)
    {
        maxRotation = val;
    }

  protected:
    virtual void
    checkParams() const;

    virtual bool
    computeImpl(const Ptr<OdometryFrame>& srcFrame, const Ptr<OdometryFrame>& dstFrame, Mat& Rt,
                const Mat& initRt) const;

    // Some params have commented desired type. It's due to AlgorithmInfo::addParams does not support it now.
    /*float*/
    double minDepth, maxDepth, maxDepthDiff;
    /*vector<int>*/
    Mat iterCounts;
    /*vector<float>*/
    Mat minGradientMagnitudes;
    double maxPointsPart;

    Mat cameraMatrix;
    int transformType;

    double maxTranslation, maxRotation;
  };

  /** Odometry based on the paper "KinectFusion: Real-Time Dense Surface Mapping and Tracking",
   * Richard A. Newcombe, Andrew Fitzgibbon, at al, SIGGRAPH, 2011.
   */
  class ICPOdometry: public Odometry
  {
  public:
    ICPOdometry();
    /** Constructor.
     * @param cameraMatrix Camera matrix
     * @param minDepth Pixels with depth less than minDepth will not be used
     * @param maxDepth Pixels with depth larger than maxDepth will not be used
     * @param maxDepthDiff Correspondences between pixels of two given frames will be filtered out
     *                     if their depth difference is larger than maxDepthDiff
     * @param maxPointsPart The method uses a random pixels subset of size frameWidth x frameHeight x pointsPart
     * @param iterCounts Count of iterations on each pyramid level.
     * @param transformType Class of trasformation
     */
    ICPOdometry(const Mat& cameraMatrix, float minDepth = DEFAULT_MIN_DEPTH(), float maxDepth = DEFAULT_MAX_DEPTH(),
                float maxDepthDiff = DEFAULT_MAX_DEPTH_DIFF(), float maxPointsPart = DEFAULT_MAX_POINTS_PART(),
                const std::vector<int>& iterCounts = std::vector<int>(), int transformType = RIGID_BODY_MOTION);

    virtual Size prepareFrameCache(Ptr<OdometryFrame>& frame, int cacheType) const;

    cv::Mat getCameraMatrix() const
    {
        return cameraMatrix;
    }
    void setCameraMatrix(const cv::Mat &val)
    {
        cameraMatrix = val;
    }
    double getMinDepth() const
    {
        return minDepth;
    }
    void setMinDepth(double val)
    {
        minDepth = val;
    }
    double getMaxDepth() const
    {
        return maxDepth;
    }
    void setMaxDepth(double val)
    {
        maxDepth = val;
    }
    double getMaxDepthDiff() const
    {
        return maxDepthDiff;
    }
    void setMaxDepthDiff(double val)
    {
        maxDepthDiff = val;
    }
    cv::Mat getIterationCounts() const
    {
        return iterCounts;
    }
    void setIterationCounts(const cv::Mat &val)
    {
        iterCounts = val;
    }
    double getMaxPointsPart() const
    {
        return maxPointsPart;
    }
    void setMaxPointsPart(double val)
    {
        maxPointsPart = val;
    }
    int getTransformType() const
    {
        return transformType;
    }
    void setTransformType(int val)
    {
        transformType = val;
    }
    double getMaxTranslation() const
    {
        return maxTranslation;
    }
    void setMaxTranslation(double val)
    {
        maxTranslation = val;
    }
    double getMaxRotation() const
    {
        return maxRotation;
    }
    void setMaxRotation(double val)
    {
        maxRotation = val;
    }
    Ptr<RgbdNormals> getNormalsComputer() const
    {
        return normalsComputer;
    }

  protected:
    virtual void
    checkParams() const;

    virtual bool
    computeImpl(const Ptr<OdometryFrame>& srcFrame, const Ptr<OdometryFrame>& dstFrame, Mat& Rt,
                const Mat& initRt) const;

    // Some params have commented desired type. It's due to AlgorithmInfo::addParams does not support it now.
    /*float*/
    double minDepth, maxDepth, maxDepthDiff;
    /*float*/
    double maxPointsPart;
    /*vector<int>*/
    Mat iterCounts;

    Mat cameraMatrix;
    int transformType;

    double maxTranslation, maxRotation;

    mutable Ptr<RgbdNormals> normalsComputer;
  };

  /** Odometry that merges RgbdOdometry and ICPOdometry by minimize sum of their energy functions.
   */

  class RgbdICPOdometry: public Odometry
  {
  public:
    RgbdICPOdometry();
    /** Constructor.
     * @param cameraMatrix Camera matrix
     * @param minDepth Pixels with depth less than minDepth will not be used
     * @param maxDepth Pixels with depth larger than maxDepth will not be used
     * @param maxDepthDiff Correspondences between pixels of two given frames will be filtered out
     *                     if their depth difference is larger than maxDepthDiff
     * @param maxPointsPart The method uses a random pixels subset of size frameWidth x frameHeight x pointsPart
     * @param iterCounts Count of iterations on each pyramid level.
     * @param minGradientMagnitudes For each pyramid level the pixels will be filtered out
     *                              if they have gradient magnitude less than minGradientMagnitudes[level].
     * @param transformType Class of trasformation
     */
    RgbdICPOdometry(const Mat& cameraMatrix, float minDepth = DEFAULT_MIN_DEPTH(), float maxDepth = DEFAULT_MAX_DEPTH(),
                    float maxDepthDiff = DEFAULT_MAX_DEPTH_DIFF(), float maxPointsPart = DEFAULT_MAX_POINTS_PART(),
                    const std::vector<int>& iterCounts = std::vector<int>(),
                    const std::vector<float>& minGradientMagnitudes = std::vector<float>(),
                    int transformType = RIGID_BODY_MOTION);

    virtual Size prepareFrameCache(Ptr<OdometryFrame>& frame, int cacheType) const;

    cv::Mat getCameraMatrix() const
    {
        return cameraMatrix;
    }
    void setCameraMatrix(const cv::Mat &val)
    {
        cameraMatrix = val;
    }
    double getMinDepth() const
    {
        return minDepth;
    }
    void setMinDepth(double val)
    {
        minDepth = val;
    }
    double getMaxDepth() const
    {
        return maxDepth;
    }
    void setMaxDepth(double val)
    {
        maxDepth = val;
    }
    double getMaxDepthDiff() const
    {
        return maxDepthDiff;
    }
    void setMaxDepthDiff(double val)
    {
        maxDepthDiff = val;
    }
    double getMaxPointsPart() const
    {
        return maxPointsPart;
    }
    void setMaxPointsPart(double val)
    {
        maxPointsPart = val;
    }
    cv::Mat getIterationCounts() const
    {
        return iterCounts;
    }
    void setIterationCounts(const cv::Mat &val)
    {
        iterCounts = val;
    }
    cv::Mat getMinGradientMagnitudes() const
    {
        return minGradientMagnitudes;
    }
    void setMinGradientMagnitudes(const cv::Mat &val)
    {
        minGradientMagnitudes = val;
    }
    int getTransformType() const
    {
        return transformType;
    }
    void setTransformType(int val)
    {
        transformType = val;
    }
    double getMaxTranslation() const
    {
        return maxTranslation;
    }
    void setMaxTranslation(double val)
    {
        maxTranslation = val;
    }
    double getMaxRotation() const
    {
        return maxRotation;
    }
    void setMaxRotation(double val)
    {
        maxRotation = val;
    }
    Ptr<RgbdNormals> getNormalsComputer() const
    {
        return normalsComputer;
    }

  protected:
    virtual void
    checkParams() const;

    virtual bool
    computeImpl(const Ptr<OdometryFrame>& srcFrame, const Ptr<OdometryFrame>& dstFrame, Mat& Rt,
                const Mat& initRt) const;

    // Some params have commented desired type. It's due to AlgorithmInfo::addParams does not support it now.
    /*float*/
    double minDepth, maxDepth, maxDepthDiff;
    /*float*/
    double maxPointsPart;
    /*vector<int>*/
    Mat iterCounts;
    /*vector<float>*/
    Mat minGradientMagnitudes;

    Mat cameraMatrix;
    int transformType;

    double maxTranslation, maxRotation;

    mutable Ptr<RgbdNormals> normalsComputer;
  };

  /** Warp the image: compute 3d points from the depth, transform them using given transformation,
   * then project color point cloud to an image plane.
   * This function can be used to visualize results of the Odometry algorithm.
   * @param image The image (of CV_8UC1 or CV_8UC3 type)
   * @param depth The depth (of type used in depthTo3d fuction)
   * @param mask The mask of used pixels (of CV_8UC1), it can be empty
   * @param Rt The transformation that will be applied to the 3d points computed from the depth
   * @param cameraMatrix Camera matrix
   * @param distCoeff Distortion coefficients
   * @param warpedImage The warped image.
   * @param warpedDepth The warped depth.
   * @param warpedMask The warped mask.
   */
  CV_EXPORTS
  void
  warpFrame(const Mat& image, const Mat& depth, const Mat& mask, const Mat& Rt, const Mat& cameraMatrix,
            const Mat& distCoeff, Mat& warpedImage, Mat* warpedDepth = 0, Mat* warpedMask = 0);

// TODO Depth interpolation
// Curvature
// Get rescaleDepth return dubles if asked for

//! @}

} /* namespace rgbd */
} /* namespace cv */

#include "linemod.hpp"

#endif /* __cplusplus */
#endif

/* End of file. */

