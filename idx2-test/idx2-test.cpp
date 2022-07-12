// To use the single-file header-only library
#define idx2_Implementation
#include "idx2.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <memory>
#include <string>
#include <vector>


/*
* Data description:
* Each file contains the data for one face, on one depth, and for 32 time steps (or 1024 time steps on NAS)
* The file path will be of the form "llc2160/u-face-3-depth-51-time-0-1024.idx2" (dataset name = llc2160, field name = u, face 3, depth 51, time steps [0..1024]
* In particular, each .idx2 dataset stores a single face (indexed from 0 to 4), for a single depth, and for 1024 time steps.
* The grid size for each .idx2 dataset is thus 2160(x) * 6480(y) * 1024(t) (for faces 0, 1), 2160(x) * 2160(y) * 1024(t) (for face 2), and 6480(x) * 2160(y) * 1024(t) (for faces 3, 4)
* Note that we do not rotate or flip any face from their original form.
*/


struct input
{
  std::string InFile; // e.g., "llc2160/u-face-3-depth-51-time-0-1024.idx2" (ALWAYS include the parent dir, not just the name of the .idx2 file)
  idx2::extent Extent; // "crop" the output to a region in the [x, y, t] space, leave as default to get whole volume
};


struct output
{
  idx2::grid OutGrid; // the logical grid of the output buffer (to get the dimensions of the grid, call idx2::v3i Dims3 = Dims(*OutGrid))
  idx2::buffer OutBuffer; // the output data buffer, if the buffer is preallocated, we will reuse that buffer
  idx2::dtype DataType; // float32, float64 etc
  virtual ~output()
  {
    if (OutBuffer)
      idx2::DeallocBuf(&OutBuffer);
  }
};


/*
* When accessing the data, we can provide three sets of parameters:
*   - the downsampling factor (in x/y/t),
*   - the accuracy (an error value, with 0 meaning no error), and
*   - the spatial-temporal extent to query data from.
* The downsampling factor is given by a vector of three integers (idx2::v3i).
* Downsampling factor (0, 0, 0) means return everything at full resolution.
* Downsampling factor (0, 1, 2) means x is full resolution, y is half resolution, and t (time) is quarter resolution.
* Accuracy is a floating-point number to indicate the desired root-mean-square error (0 means near-lossless).
* The downsampling factor also affects the accuracy, but the Accuracy parameter is to be interpreted as if there is no downsampling.
* The Extent parameter (of type idx2::extent) determines where in the [x, y, t] space we want to query from.
* For example, to query face 0 at time step 500, we can set the extent to be from [0, 0, 500] to [2159, 6479, 500].
* This can be done by using the idx2::extent constructor idx2::extent(idx2::v3i(0, 0, 500), idx2::v3i(2160, 6480, 1)).
* If a default idx2::extent is given, it is understood that the full volume is requested (e.g., from [0, 0, 0] to [2159, 6479, 1023] for face 0).
*
* There are two parameters, OutGrid (of type idx2::grid) and OutBuf (of type idx2::buffer).
* To see what they mean, consider the scenarios below:
*
* 1) In the first scenario, we have a 2D 7x5 grid.
* The extent we are asking for is from [1, 1] to [4, 3].
* The OutGrid will be a sub-grid of samples, from [1, 1] to [4, 3], with strides [1, 1], for a total of 4x3 samples.
* We use @ to denote the samples inside OutGrid (that will be returned to the user).
* The OutBuf will be a linear buffer of 4x3=12 floating-point numbers, storing the sample values in the OutGrid.
*
*     +    +    +    +    +    +    +
*
*     +    @----@----@----@    +    +
*          |              |
*     +    @    @    @    @    +    +
*          |              |
*     +    @----@----@----@    +    +
*
*     +    +    +    +    +    +    +
*
* 2) In the second scenario, we still have the same 7x5 grid.
* The extent we are asking for is still from [1, 1] to [4, 3], as above.
* But now we are using a downsampling factor of (1, 0), meaning we now only get every other sample in X.
* Below we show the downsampled grid according to downsampling factor (1, 0).
* Note that the (coarse) samples that fall inside the queried extent do not "cover" all of this extent.
*
*     +         +         +         +
*
*     +    -----+---------+         +
*          |              |
*     +    |    +         +         +
*          |              |
*     +    -----+---------+         +
*
*     +         +         +         +
*
* Therefore, we enlarge the extent so that it "snaps" to the downsampled grid (see below).
* As a result, the OutGrid is now from [0, 1] to [4, 3], with strides [2, 1], for a total of 3x3 samples (see the @ samples below).
* The OutBuf will be a linear buffer of 3x3=9 floating-point numbers, storing the sample values in the OutGrid.
*
*     +    +    +    +    +    +    +
*
*     @----+----@----+----@    +    +
*     |                   |
*     @    +    @    +    @    +    +
*     |                   |
*     @----+----@----+----@    +    +
*
*     +    +    +    +    +    +    +
*
* 3) In the second scenario, we still have the same 7x5 grid.
* The extent we are asking for is now from [1, 0] to [1, 4] (i.e., a "slicing" operation along X)
* We are stil using a downsampling factor of (1, 0), meaning we now only get every other sample in X.
* In this case, our query extent "falls between" the samples of the downsampled grid.
*
*     +    +    +    +    +    +    +
*          |
*     +    +    +    +    +    +    +
*          |
*     +    +    +    +    +    +    +
*          |
*     +    +    +    +    +    +    +
*          |
*     +    +    +    +    +    +    +
*
* As before, we enlarge the requested extent so that it "snaps" to the downsampled grid.
*
*     @---------@         +         +
*     |         |
*     @         @         +         +
*     |         |
*     @         @         +         +
*     |         |
*     @         @         +         +
*     |         |
*     @---------@         +         +
*
* The dimensions of OutGrid will be 2x5, and OutBuf will contain 10 samples.
* Note that even though the user asks for a 1x5 slice, we are returning a 2x5 sub-grid.
* To get the slice that they want, the user then can choose to do either:
*   - Pick one of the two returned slices
*   - Interpolate between the two returned slices
*/
idx2::error<idx2::idx2_err_code>
DecodeOneFile(const std::string& InDir, // e.g., "/nobackupp19/vpascucc/converted_files" (an absolute or relative path that leads to the parent dir of the .idx2 file, can also simply be ".")
              const input& Input, // see struct input above
              const idx2::v3i& Downsampling3, // e.g., (1, 1, 2) (meaning half x, half y, quarter t)
              double Accuracy, // e.g., 0.01
              output* Output)
{
  assert(Output != nullptr);

  // First, we initialize the parameters
  idx2::params P;
  P.InputFile = Input.InFile.c_str();
  P.InDir = InDir.c_str();
  idx2::idx2_file Idx2;
  idx2_CleanUp(Dealloc(&Idx2)); // clean up Idx2 automatically
  idx2_PropagateIfError(Init(&Idx2, P));

  // Next, we compute the output grid
  P.DownsamplingFactor3 = Downsampling3;
  P.DecodeAccuracy = Accuracy;
  if (idx2::Dims(Input.Extent) == idx2::v3i(0))
    P.DecodeExtent = idx2::extent(Idx2.Dims3); // get the whole volume
  else
    P.DecodeExtent = Input.Extent;
  Output->OutGrid = idx2::GetOutputGrid(Idx2, P);

  // If the output buffer is uninitialized, we allocate it
  idx2::i64 MinBufSize = idx2::SizeOf(Idx2.DType) * idx2::Prod<idx2::i64>(idx2::Dims(Output->OutGrid));
  if (!Output->OutBuffer && idx2::Dims(Output->OutGrid) > 0)
    idx2::AllocBuf(&Output->OutBuffer, MinBufSize);
  // If the output buffer is preallocated by the user, we check if it is too small
  idx2_ReturnErrorIf(Output->OutBuffer.Bytes < MinBufSize, idx2::err_code::SizeTooSmall, "Output buffer is too small\n");

  // Finally, we decode and return the queried data
  idx2_PropagateIfError(idx2::Decode(&Idx2, P, &Output->OutBuffer)); // the output is stored in OutBuffer
  Output->DataType = Idx2.DType;

  return idx2_Error(idx2::idx2_err_code::NoError); // make sure to check for return error at call site
}


idx2::error<idx2::idx2_err_code>
GetOutputGrid(const std::string& InDir, // e.g., "/nobackupp19/vpascucc/converted_files" (an absolute or relative path that leads to the parent dir of the .idx2 file, can also simply be ".")
              const input& Input, // see struct input above
              const idx2::v3i& Downsampling3, // e.g., (1, 1, 2) (meaning half x, half y, quarter t)
              idx2::grid* OutGrid)
{
  assert(OutGrid != nullptr);

  // First, we initialize the parameters
  idx2::params P;
  P.InputFile = Input.InFile.c_str();
  P.InDir = InDir.c_str();
  idx2::idx2_file Idx2;
  idx2_CleanUp(Dealloc(&Idx2)); // clean up Idx2 automatically
  idx2_PropagateIfError(Init(&Idx2, P));

  // Next, we compute the output grid
  P.DownsamplingFactor3 = Downsampling3;
  if (idx2::Dims(Input.Extent) == idx2::v3i(0))
    P.DecodeExtent = idx2::extent(Idx2.Dims3); // get the whole volume
  else
    P.DecodeExtent = Input.Extent;
  *OutGrid = idx2::GetOutputGrid(Idx2, P);

  return idx2_Error(idx2::idx2_err_code::NoError); // make sure to check for return error at call site
}


/* Get potentially multiple faces at multiple depths */
// TODO: we can use multiple threads, one for each file
// TODO: think about error handling (what if the input file does not exist)
// how about this compared to caching the idx2 struct?
idx2::error<idx2::idx2_err_code>
DecodeMultipleFiles(const std::string& InDir,
                    const std::vector<input>& Inputs,
                    const idx2::v3i& Downsampling3,
                    double Accuracy,
                    std::vector<output>* Outputs)
{
  idx2_Assert(!Inputs.empty(), "Input cannot be empty\n");
  idx2_Assert(Inputs.size() == Outputs->size());

  /* duplicate the file names so that we can sort them (but remember the original order for the outputs) */
  std::vector<std::pair<input, int>> SortedInputs(Inputs.size());
  for (int I = 0; I < Inputs.size(); ++I) {
    SortedInputs[I] = std::make_pair(Inputs[I], I);
  }
  std::sort(SortedInputs.begin(), SortedInputs.end(), [](const auto& P1, const auto& P2) {
    return P1.first.InFile < P2.first.InFile;
  });

  int Begin = 0;
  for (int I = 1; I <= SortedInputs.size(); ++I) {
    if (I < SortedInputs.size() && SortedInputs[I].first.InFile == SortedInputs[I - 1].first.InFile) {
      continue;
    }

    /* construct input and output for a single query */
    idx2::extent Extent = SortedInputs[Begin].first.Extent;
    for (int J = Begin; J < I; ++J) {
      Extent = idx2::BoundingBox(Extent, SortedInputs[J].first.Extent); // accumulate extent
    }
    input Input{ SortedInputs[Begin].first.InFile, Extent };
    output Output;
    idx2_PropagateIfError(DecodeOneFile(InDir, Input, Downsampling3, Accuracy, &Output));

    /* now distribute the output */
    for (int J = Begin; J < I; ++J) {
      output& OutputJ = (*Outputs)[SortedInputs[J].second];
      GetOutputGrid(InDir, SortedInputs[J].first, Downsampling3, &(OutputJ.OutGrid));
      OutputJ.DataType = Output.DataType;

      idx2::i64 MinBufSize = idx2::SizeOf(Output.DataType) * idx2::Prod<idx2::i64>(idx2::Dims(OutputJ.OutGrid));
      if (!OutputJ.OutBuffer && idx2::Dims(OutputJ.OutGrid) > 0)
        idx2::AllocBuf(&OutputJ.OutBuffer, MinBufSize);
      // If the output buffer is preallocated by the user, we check if it is too small
      // TODO: just automatically reallocate if necessary
      idx2_ReturnErrorIf(OutputJ.OutBuffer.Bytes < MinBufSize, idx2::err_code::SizeTooSmall, "Output buffer is too small\n");

      idx2::extent FromE = idx2::Relative(Output.OutGrid, Output.OutGrid);
      idx2::volume FromV = idx2::volume(Output.OutBuffer, idx2::Dims(FromE), Output.DataType);
      idx2::extent ToE   = idx2::Relative(OutputJ.OutGrid, Output.OutGrid);
      idx2::volume ToV   = idx2::volume(OutputJ.OutBuffer, idx2::Dims(ToE), OutputJ.DataType);
      idx2::CopyExtentExtent<float, float>(FromE, FromV, ToE, &ToV); // TODO: hard-coding the types
    }
    Begin = I;
  }
  return idx2_Error(idx2::idx2_err_code::NoError);
}


/* [Begin, End) range (End is exclusive, hence the open bracket) */
struct range
{
  int Begin = 0;
  int End = 0;
};


/* Specify a face range as well as X and Y ranges within the faces. Useful for vertical slicing, for instance. */
struct spatial_range
{
  int Face;
  range XRange;
  range YRange;
};


/* The relative order of Time/Face/Depth in the output buffer */
enum class order
{
  DepthFaceTime, // Time varies fastest, then Face, then Depth
  DepthTimeFace,
  FaceTimeDepth,
  FaceDepthTime,
  TimeDepthFace,
  TimeFaceDepth
};


enum class slice_type
{
  AlongX, AlongY, RotatedAlongX, RotatedAlongY
};


struct query_info
{
  /* Parameters, needs to be changed if the default values below do not apply */
  std::string NameFormat = "llc2160/u-face-%d-depth-%d-time-%d-%d.idx2"; // TODO: create an API to change this
  std::string InDir = "/nobackupp19/vpascucc/converted_files"; // contain the relative/absolute path to the NameFormat above // TODO: create an API to change this
  int TimeGroup = 1024; // every 1024 time steps are grouped into one .idx2 file

  /* The following needs to be initialized before a query_info can be used */
  std::vector<spatial_range> SpatialRanges;
  range TimeRange;
  range DepthRange;
  order Order = order::DepthFaceTime; // TODO: create an API to control this

  idx2::v3i Downsampling3;
  double Accuracy = 0.01;

  virtual const int N() const = 0;
  virtual const int NumFaces() const = 0;
  virtual const idx2::v3i* FaceDims3() const = 0; // get the dimensions of the faces


  virtual void SetNameFormat(const std::string& NameFormat)
  {
    this->NameFormat = NameFormat;
  }


  virtual void SetInputDirectory(const std::string& InDir)
  {
    this->InDir = InDir;
  }


  virtual void SetTimeGroup(int TimeGroup)
  {
    this->TimeGroup = TimeGroup;
  }


  virtual void SetTimeRange(int TimeBegin, int TimeEnd)
  {
    TimeRange.Begin = TimeBegin;
    TimeRange.End = TimeEnd;
  }


  virtual void SetDepthRange(int DepthBegin, int DepthEnd)
  {
    DepthRange.Begin = DepthBegin;
    DepthRange.End = DepthEnd;
  }


  virtual void SetOrder(order Order)
  {
    this->Order = Order;
  }

  virtual void SetDownsamplingFactor(int DownsamplingX, int DownsamplingY, int DownsamplingTime)
  {
    this->Downsampling3 = idx2::v3i(DownsamplingX, DownsamplingY, DownsamplingTime);
  }


  virtual void SetAccuracy(double Accuracy)
  {
    this->Accuracy = Accuracy;
  }


  virtual void AddSpatialRange(int Face, int XBegin, int XEnd, int YBegin, int YEnd)
  {
    SpatialRanges.push_back(spatial_range{ Face, range{XBegin, XEnd}, range{YBegin, YEnd} });
  }


  virtual void AddFace(int Face)
  {
    const idx2::v3i& D3 = FaceDims3()[Face];
    SpatialRanges.push_back(spatial_range{ Face, range{0, D3.X}, range{0, D3.Y}});
  }


  virtual void AddFaceSlice(int Face, slice_type SliceType, int Position)
  {
    const idx2::v3i& D3 = FaceDims3()[Face];
    if (SliceType == slice_type::AlongX)
      SpatialRanges.push_back(spatial_range{ Face, range{0, D3.X}, range{Position, Position + 1}});
    else if (SliceType == slice_type::AlongY)
      SpatialRanges.push_back(spatial_range{ Face, range{Position, Position + 1}, range{0, D3.Y}});
    else if (SliceType == slice_type::RotatedAlongX)
      AddFaceSlice(Face, slice_type::AlongY, D3.X - Position);
    else if (SliceType == slice_type::RotatedAlongY)
      AddFaceSlice(Face, slice_type::AlongX, Position);
  }


  virtual bool Verify() const
  {
    for (const auto& R : SpatialRanges) {
      if (R.XRange.Begin >= R.XRange.End) {
        printf("X range: [%d %d) is invalid\n", R.XRange.Begin, R.XRange.End);
        return false;
      }
      if (R.YRange.Begin >= R.YRange.End) {
        printf("Y range: [%d %d) is invalid\n", R.YRange.Begin, R.YRange.End);
        return false;
      }
    }

    if (TimeRange.Begin >= TimeRange.End) {
      printf("Time range: [%d %d) is invalid\n", TimeRange.Begin, TimeRange.End);
      return false;
    }

    if (DepthRange.Begin >= DepthRange.End) {
      printf("Depth range: [%d %d) is invalid\n", DepthRange.Begin, DepthRange.End);
      return false;
    }

    return true;
  }
};


struct llc_2160_query_info : public query_info
{
  virtual const int N() const override
  {
    return 2160; // TODO: allow the user to change thid
  }


  virtual const int NumFaces() const override
  {
    return 5;
  }


  virtual const idx2::v3i* FaceDims3() const override
  {
    static constexpr int N = 2160; // TODO: allow the user to change this
    static constexpr idx2::v3i FaceDims3[5] = { idx2::v3i(N, 3 * N, 1),
                                                idx2::v3i(N, 3 * N, 1),
                                                idx2::v3i(N,     N, 1),
                                                idx2::v3i(3 * N, N, 1),
                                                idx2::v3i(3 * N, N, 1) };
    return FaceDims3;
  }


  virtual bool Verify() const override
  {
    // TODO: write this (verify theat x and y are withiin the range)
    return true;
  }


  int SkipCapFace(int F) const
  {
    if (F > 2)
      return F + 1;
    return F;
  }
};


struct output_metadata
{
  int Face;
  int Depth;
  int Time;
};


idx2::v3i GetStrides(int NumFaces, int NumDepths, int NumTimes, order Order)
{
  int FaceStride = 1, DepthStride = 1, TimeStride = 1;
  switch (Order) {
  case order::DepthFaceTime:
    TimeStride = 1; FaceStride = NumTimes; DepthStride = NumFaces * NumTimes;
    break;
  case order::DepthTimeFace:
    FaceStride = 1; TimeStride = NumFaces; DepthStride = NumTimes * NumFaces;
    break;
  case order::FaceDepthTime:
    TimeStride = 1; DepthStride = NumTimes; FaceStride = NumDepths * NumTimes;
    break;
  case order::FaceTimeDepth:
    DepthStride = 1; TimeStride = NumDepths; FaceStride = NumTimes * NumDepths;
    break;
  case order::TimeDepthFace:
    FaceStride = 1; DepthStride = NumFaces; TimeStride = NumDepths * NumFaces;
    break;
  case order::TimeFaceDepth:
    DepthStride = 1; FaceStride = NumDepths; TimeStride = NumFaces * NumDepths;
    break;
  default:
    idx2_Assert(false);
  }

  return idx2::v3i(FaceStride, DepthStride, TimeStride);
}


idx2::error<idx2::idx2_err_code>
ExecuteQuery(const query_info& QueryInfo,
             std::vector<output>* Outputs,
             std::vector<output_metadata>* OutputsMetadata)
{
  idx2_ReturnErrorIf(!QueryInfo.Verify(), idx2::err_code::DimensionMismatched);
  const int NumDepths = QueryInfo.DepthRange.End - QueryInfo.DepthRange.Begin;
  const int NumTimes = QueryInfo.TimeRange.End - QueryInfo.TimeRange.Begin;
  const int NumFaces = QueryInfo.SpatialRanges.size();
  std::vector<input> Inputs(NumDepths * NumFaces * NumTimes);
  Outputs->resize(Inputs.size());
  OutputsMetadata->resize(Inputs.size());
  idx2::v3i Strides3 = GetStrides(NumFaces, NumDepths, NumTimes, QueryInfo.Order);
  int FaceStride = Strides3.X;
  int DepthStride = Strides3.Y;
  int TimeStride = Strides3.Z;
  for (int D = 0; D + QueryInfo.DepthRange.Begin < QueryInfo.DepthRange.End; ++D) {
    int Depth = QueryInfo.DepthRange.Begin + D;
    for (int F = 0; F < QueryInfo.SpatialRanges.size(); ++F) {
      for (int T = 0; T+ QueryInfo.TimeRange.Begin < QueryInfo.TimeRange.End; ++T) {
        int Time = QueryInfo.TimeRange.Begin + T;
        int Index = T * TimeStride + F * FaceStride + D * DepthStride;
        const spatial_range& R = QueryInfo.SpatialRanges[F];
        Inputs[Index].Extent = idx2::extent(idx2::v3i(R.XRange.Begin, R.YRange.Begin, Time), idx2::v3i(R.XRange.End - R.XRange.Begin, R.YRange.End - R.YRange.Begin, 1));
        int TimeBegin = Time / QueryInfo.TimeGroup;
        int TimeEnd = TimeBegin + QueryInfo.TimeGroup;
        Inputs[Index].InFile.resize(256);
        sprintf(Inputs[Index].InFile.data(), QueryInfo.NameFormat.data(), R.Face, Depth, TimeBegin, TimeEnd);

        (*OutputsMetadata)[Index].Depth = Depth;
        (*OutputsMetadata)[Index].Time = Time;
        (*OutputsMetadata)[Index].Face = R.Face;
      }
    }
  }
  idx2_PropagateIfError(DecodeMultipleFiles(QueryInfo.InDir, Inputs, QueryInfo.Downsampling3, QueryInfo.Accuracy, Outputs));
  // TODO: how do we free the buffers
}


/* Do vertical slicing */
idx2::error<idx2::idx2_err_code>
VerticalSlicingExample()
{
  // TODO: either interpolate or snap the slice to one

  /* We first slice faces 0, 1, 3, 4 along X axis, at Y = 3000, for time step 16 */
  llc_2160_query_info QueryInfo;
  //QueryInfo.SetNameFormat("llc2160/u-face-%d-depth-%d-time-%d-%d.idx2");
  //QueryInfo.SetInputDirectory("/nobackupp19/vpascucc/converted_files");
  QueryInfo.SetNameFormat("D:/Datasets/nasa/llc_2160_32/llc2160/u-face-%d-depth-%d-time-%d-%d.idx2");
  QueryInfo.SetInputDirectory("D:/Datasets/nasa/llc_2160_32");
  QueryInfo.SetTimeGroup(32);
  QueryInfo.SetDepthRange(0, 90);
  QueryInfo.SetTimeRange(16, 17);
  QueryInfo.SetOrder(order::TimeDepthFace);
  QueryInfo.SetDownsamplingFactor(0, 0, 0);
  QueryInfo.SetAccuracy(0.01);

  std::vector<output> Outputs;
  std::vector<output_metadata> OutputsMetadata;

  std::array<int, 4> Faces = { 0, 1, 3, 4 }; // all the "lat-lon" faces
  int SlicePosition = 3000; // Y coordinate between [0, 6479]
  for (int I = 0; I < Faces.size(); ++I) {
    if (Faces[I] < 2)
      QueryInfo.AddFaceSlice(Faces[I], slice_type::AlongX, SlicePosition);
    else if (Faces[I] > 2) // for faces 3 and 4, we need to "rotate" the slice
      QueryInfo.AddFaceSlice(Faces[I], slice_type::RotatedAlongX, SlicePosition);
  }
  auto Result = ExecuteQuery(QueryInfo, &Outputs, &OutputsMetadata);
  if (!Result) {
    fprintf(stderr, "%s\n", ToString(Result));                                                   \
      return Result;
  }

  return idx2_Error(idx2::err_code::NoError);
}


int main()
{
  VerticalSlicingExample();
  // vertical slicing across time
  // get five faces across time at a certain depth
  // get five faces across depths at a certain time
  // get five faces across multiple depths and time

	return 0;
}

