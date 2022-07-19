; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.GCState = type { i8*, i8*, i8, i64, i64, %struct.ObjectHeader*, i8*, i8*, i64, i64, i64, i8 }
%struct.ObjectHeader = type { i64, %struct.ObjectHeader*, void (i8*)* }
%struct.__crt_locale_pointers = type { %struct.__crt_locale_data*, %struct.__crt_multibyte_data* }
%struct.__crt_locale_data = type opaque
%struct.__crt_multibyte_data = type opaque
%struct._iobuf = type { i8* }
%struct.Frame = type { i64, i64, %struct.Frame*, [0 x %struct.ObjectHeader**] }
%struct.ThreadStartInfo = type { i64 (i8*, i8*)*, i8* }
%struct._SECURITY_ATTRIBUTES = type { i32, i8*, i32 }

$sprintf = comdat any

$vsprintf = comdat any

$_snprintf = comdat any

$_vsnprintf = comdat any

$printf = comdat any

$_vsprintf_l = comdat any

$_vsnprintf_l = comdat any

$__local_stdio_printf_options = comdat any

$_vfprintf_l = comdat any

$"??_C@_0CB@DALJHOPI@we?5REALLY?5shouldn?8t?5be?5here?0?5?$CFp?6@" = comdat any

$"??_C@_03OFAPEBGM@?$CFs?6?$AA@" = comdat any

$"??_C@_06IKJDLJAH@?$CFs?5?$CFp?6?$AA@" = comdat any

@gc_state = dso_local global %struct.GCState zeroinitializer, align 8
@"??_C@_0CB@DALJHOPI@we?5REALLY?5shouldn?8t?5be?5here?0?5?$CFp?6@" = linkonce_odr dso_local unnamed_addr constant [33 x i8] c"we REALLY shouldn't be here, %p\0A\00", comdat, align 1
@"??_C@_03OFAPEBGM@?$CFs?6?$AA@" = linkonce_odr dso_local unnamed_addr constant [4 x i8] c"%s\0A\00", comdat, align 1
@"??_C@_06IKJDLJAH@?$CFs?5?$CFp?6?$AA@" = linkonce_odr dso_local unnamed_addr constant [7 x i8] c"%s %p\0A\00", comdat, align 1
@__local_stdio_printf_options._OptionsStorage = internal global i64 0, align 8

; Function Attrs: nobuiltin noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @sprintf(i8* %0, i8* %1, ...) #0 comdat {
  %3 = alloca i8*, align 8
  %4 = alloca i8*, align 8
  %5 = alloca i32, align 4
  %6 = alloca i8*, align 8
  store i8* %1, i8** %3, align 8
  store i8* %0, i8** %4, align 8
  %7 = bitcast i8** %6 to i8*
  call void @llvm.va_start(i8* %7)
  %8 = load i8*, i8** %6, align 8
  %9 = load i8*, i8** %3, align 8
  %10 = load i8*, i8** %4, align 8
  %11 = call i32 @_vsprintf_l(i8* %10, i8* %9, %struct.__crt_locale_pointers* null, i8* %8)
  store i32 %11, i32* %5, align 4
  %12 = bitcast i8** %6 to i8*
  call void @llvm.va_end(i8* %12)
  %13 = load i32, i32* %5, align 4
  ret i32 %13
}

; Function Attrs: nobuiltin noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @vsprintf(i8* %0, i8* %1, i8* %2) #0 comdat {
  %4 = alloca i8*, align 8
  %5 = alloca i8*, align 8
  %6 = alloca i8*, align 8
  store i8* %2, i8** %4, align 8
  store i8* %1, i8** %5, align 8
  store i8* %0, i8** %6, align 8
  %7 = load i8*, i8** %4, align 8
  %8 = load i8*, i8** %5, align 8
  %9 = load i8*, i8** %6, align 8
  %10 = call i32 @_vsnprintf_l(i8* %9, i64 -1, i8* %8, %struct.__crt_locale_pointers* null, i8* %7)
  ret i32 %10
}

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_snprintf(i8* %0, i64 %1, i8* %2, ...) #1 comdat {
  %4 = alloca i8*, align 8
  %5 = alloca i64, align 8
  %6 = alloca i8*, align 8
  %7 = alloca i32, align 4
  %8 = alloca i8*, align 8
  store i8* %2, i8** %4, align 8
  store i64 %1, i64* %5, align 8
  store i8* %0, i8** %6, align 8
  %9 = bitcast i8** %8 to i8*
  call void @llvm.va_start(i8* %9)
  %10 = load i8*, i8** %8, align 8
  %11 = load i8*, i8** %4, align 8
  %12 = load i64, i64* %5, align 8
  %13 = load i8*, i8** %6, align 8
  %14 = call i32 @_vsnprintf(i8* %13, i64 %12, i8* %11, i8* %10)
  store i32 %14, i32* %7, align 4
  %15 = bitcast i8** %8 to i8*
  call void @llvm.va_end(i8* %15)
  %16 = load i32, i32* %7, align 4
  ret i32 %16
}

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vsnprintf(i8* %0, i64 %1, i8* %2, i8* %3) #1 comdat {
  %5 = alloca i8*, align 8
  %6 = alloca i8*, align 8
  %7 = alloca i64, align 8
  %8 = alloca i8*, align 8
  store i8* %3, i8** %5, align 8
  store i8* %2, i8** %6, align 8
  store i64 %1, i64* %7, align 8
  store i8* %0, i8** %8, align 8
  %9 = load i8*, i8** %5, align 8
  %10 = load i8*, i8** %6, align 8
  %11 = load i64, i64* %7, align 8
  %12 = load i8*, i8** %8, align 8
  %13 = call i32 @_vsnprintf_l(i8* %12, i64 %11, i8* %10, %struct.__crt_locale_pointers* null, i8* %9)
  ret i32 %13
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @SWERVE_gc_allocate(i64 %0, void (i8*)* %1) #1 {
  %3 = alloca void (i8*)*, align 8
  %4 = alloca i64, align 8
  %5 = alloca %struct.ObjectHeader*, align 8
  store void (i8*)* %1, void (i8*)** %3, align 8
  store i64 %0, i64* %4, align 8
  %6 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %7 = call i32 @WaitForSingleObject(i8* %6, i32 -1)
  %8 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %9 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  %10 = getelementptr i8, i8* %8, i64 %9
  %11 = bitcast i8* %10 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %11, %struct.ObjectHeader** %5, align 8
  %12 = load i64, i64* %4, align 8
  %13 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  %14 = add i64 %13, %12
  store i64 %14, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  %15 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %16 = bitcast %struct.ObjectHeader* %15 to i8*
  %17 = load i64, i64* %4, align 8
  call void @llvm.memset.p0i8.i64(i8* align 8 %16, i8 0, i64 %17, i1 false)
  %18 = load i64, i64* %4, align 8
  %19 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %20 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %19, i32 0, i32 0
  store i64 %18, i64* %20, align 8
  %21 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %22 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %21, i32 0, i32 1
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %22, align 8
  %23 = load void (i8*)*, void (i8*)** %3, align 8
  %24 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %25 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %24, i32 0, i32 2
  store void (i8*)* %23, void (i8*)** %25, align 8
  %26 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %27 = call i32 @ReleaseMutex(i8* %26)
  %28 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %29 = bitcast %struct.ObjectHeader* %28 to i8*
  ret i8* %29
}

declare dllimport i32 @WaitForSingleObject(i8*, i32) #2

; Function Attrs: argmemonly nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #3

declare dllimport i32 @ReleaseMutex(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local %struct.ObjectHeader* @SWERVE_gc_move(%struct.ObjectHeader* %0) #1 {
  %2 = alloca %struct.ObjectHeader*, align 8
  %3 = alloca %struct.ObjectHeader*, align 8
  %4 = alloca i64, align 8
  %5 = alloca %struct.ObjectHeader*, align 8
  store %struct.ObjectHeader* %0, %struct.ObjectHeader** %3, align 8
  %6 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %7 = icmp eq %struct.ObjectHeader* %6, null
  br i1 %7, label %8, label %9

8:                                                ; preds = %1
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %2, align 8
  br label %72

9:                                                ; preds = %1
  %10 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %11 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %12 = bitcast %struct.ObjectHeader* %11 to i8*
  %13 = icmp ule i8* %10, %12
  br i1 %13, label %14, label %54

14:                                               ; preds = %9
  %15 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %16 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %17 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %18 = getelementptr i8, i8* %16, i64 %17
  %19 = bitcast i8* %18 to %struct.ObjectHeader*
  %20 = icmp ult %struct.ObjectHeader* %15, %19
  br i1 %20, label %21, label %54

21:                                               ; preds = %14
  %22 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %23 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %22, i32 0, i32 0
  %24 = load i64, i64* %23, align 8
  store i64 %24, i64* %4, align 8
  %25 = load i64, i64* %4, align 8
  %26 = icmp eq i64 %25, 0
  br i1 %26, label %27, label %31

27:                                               ; preds = %21
  %28 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %29 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %28, i32 0, i32 1
  %30 = load %struct.ObjectHeader*, %struct.ObjectHeader** %29, align 8
  store %struct.ObjectHeader* %30, %struct.ObjectHeader** %2, align 8
  br label %72

31:                                               ; preds = %21
  %32 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  %33 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), align 8
  %34 = getelementptr i8, i8* %32, i64 %33
  %35 = bitcast i8* %34 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %35, %struct.ObjectHeader** %5, align 8
  %36 = load i64, i64* %4, align 8
  %37 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), align 8
  %38 = add i64 %37, %36
  store i64 %38, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), align 8
  %39 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %40 = bitcast %struct.ObjectHeader* %39 to i8*
  %41 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %42 = bitcast %struct.ObjectHeader* %41 to i8*
  %43 = load i64, i64* %4, align 8
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 8 %40, i8* align 8 %42, i64 %43, i1 false)
  %44 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  %45 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %46 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %45, i32 0, i32 1
  store %struct.ObjectHeader* %44, %struct.ObjectHeader** %46, align 8
  %47 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  store %struct.ObjectHeader* %47, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  %48 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %49 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %48, i32 0, i32 0
  store i64 0, i64* %49, align 8
  %50 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %51 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %52 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %51, i32 0, i32 1
  store %struct.ObjectHeader* %50, %struct.ObjectHeader** %52, align 8
  %53 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  store %struct.ObjectHeader* %53, %struct.ObjectHeader** %2, align 8
  br label %72

54:                                               ; preds = %14, %9
  %55 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  %56 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %57 = bitcast %struct.ObjectHeader* %56 to i8*
  %58 = icmp ule i8* %55, %57
  br i1 %58, label %59, label %70

59:                                               ; preds = %54
  %60 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %61 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  %62 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %63 = getelementptr i8, i8* %61, i64 %62
  %64 = bitcast i8* %63 to %struct.ObjectHeader*
  %65 = icmp ult %struct.ObjectHeader* %60, %64
  br i1 %65, label %66, label %70

66:                                               ; preds = %59
  %67 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %68 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([33 x i8], [33 x i8]* @"??_C@_0CB@DALJHOPI@we?5REALLY?5shouldn?8t?5be?5here?0?5?$CFp?6@", i64 0, i64 0), %struct.ObjectHeader* %67)
  %69 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  store %struct.ObjectHeader* %69, %struct.ObjectHeader** %2, align 8
  br label %72

70:                                               ; preds = %59, %54
  %71 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  store %struct.ObjectHeader* %71, %struct.ObjectHeader** %2, align 8
  br label %72

72:                                               ; preds = %70, %66, %31, %27, %8
  %73 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  ret %struct.ObjectHeader* %73
}

; Function Attrs: argmemonly nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nobuiltin noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @printf(i8* %0, ...) #0 comdat {
  %2 = alloca i8*, align 8
  %3 = alloca i32, align 4
  %4 = alloca i8*, align 8
  store i8* %0, i8** %2, align 8
  %5 = bitcast i8** %4 to i8*
  call void @llvm.va_start(i8* %5)
  %6 = load i8*, i8** %4, align 8
  %7 = load i8*, i8** %2, align 8
  %8 = call %struct._iobuf* @__acrt_iob_func(i32 1)
  %9 = call i32 @_vfprintf_l(%struct._iobuf* %8, i8* %7, %struct.__crt_locale_pointers* null, i8* %6)
  store i32 %9, i32* %3, align 4
  %10 = bitcast i8** %4 to i8*
  call void @llvm.va_end(i8* %10)
  %11 = load i32, i32* %3, align 4
  ret i32 %11
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local %struct.ObjectHeader* @SWERVE_gc_trace_helper(i8* %0, i8* %1, %struct.ObjectHeader* %2) #1 {
  %4 = alloca %struct.ObjectHeader*, align 8
  %5 = alloca i8*, align 8
  %6 = alloca i8*, align 8
  %7 = alloca %struct.ObjectHeader*, align 8
  store %struct.ObjectHeader* %2, %struct.ObjectHeader** %4, align 8
  store i8* %1, i8** %5, align 8
  store i8* %0, i8** %6, align 8
  %8 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %9 = call %struct.ObjectHeader* @SWERVE_gc_move(%struct.ObjectHeader* %8)
  store %struct.ObjectHeader* %9, %struct.ObjectHeader** %7, align 8
  %10 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  ret %struct.ObjectHeader* %10
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local %struct.ObjectHeader* @SWERVE_gc_check(%struct.Frame* %0, %struct.ObjectHeader* %1) #1 {
  %3 = alloca %struct.ObjectHeader*, align 8
  %4 = alloca %struct.ObjectHeader*, align 8
  %5 = alloca %struct.Frame*, align 8
  %6 = alloca i64, align 8
  %7 = alloca %struct.ObjectHeader**, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca i64, align 8
  store %struct.ObjectHeader* %1, %struct.ObjectHeader** %4, align 8
  store %struct.Frame* %0, %struct.Frame** %5, align 8
  %12 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 11), align 8
  %13 = trunc i8 %12 to i1
  br i1 %13, label %14, label %16

14:                                               ; preds = %2
  %15 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  store %struct.ObjectHeader* %15, %struct.ObjectHeader** %3, align 8
  br label %70

16:                                               ; preds = %2
  %17 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  %18 = trunc i8 %17 to i1
  br i1 %18, label %19, label %68

19:                                               ; preds = %16
  %20 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %21 = call i32 @WaitForSingleObject(i8* %20, i32 -1)
  store i8 1, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 11), align 8
  %22 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %23 = call %struct.ObjectHeader* @SWERVE_gc_move(%struct.ObjectHeader* %22)
  store %struct.ObjectHeader* %23, %struct.ObjectHeader** %4, align 8
  br label %24

24:                                               ; preds = %51, %19
  %25 = load %struct.Frame*, %struct.Frame** %5, align 8
  %26 = icmp ne %struct.Frame* %25, null
  br i1 %26, label %27, label %55

27:                                               ; preds = %24
  store i64 0, i64* %6, align 8
  br label %28

28:                                               ; preds = %48, %27
  %29 = load i64, i64* %6, align 8
  %30 = load %struct.Frame*, %struct.Frame** %5, align 8
  %31 = getelementptr inbounds %struct.Frame, %struct.Frame* %30, i32 0, i32 0
  %32 = load i64, i64* %31, align 8
  %33 = icmp ult i64 %29, %32
  br i1 %33, label %34, label %51

34:                                               ; preds = %28
  %35 = load %struct.Frame*, %struct.Frame** %5, align 8
  %36 = getelementptr inbounds %struct.Frame, %struct.Frame* %35, i32 0, i32 3
  %37 = load i64, i64* %6, align 8
  %38 = getelementptr inbounds [0 x %struct.ObjectHeader**], [0 x %struct.ObjectHeader**]* %36, i64 0, i64 %37
  %39 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %38, align 8
  store %struct.ObjectHeader** %39, %struct.ObjectHeader*** %7, align 8
  %40 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %7, align 8
  %41 = icmp ne %struct.ObjectHeader** %40, null
  br i1 %41, label %42, label %47

42:                                               ; preds = %34
  %43 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %7, align 8
  %44 = load %struct.ObjectHeader*, %struct.ObjectHeader** %43, align 8
  %45 = call %struct.ObjectHeader* @SWERVE_gc_move(%struct.ObjectHeader* %44)
  %46 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %7, align 8
  store %struct.ObjectHeader* %45, %struct.ObjectHeader** %46, align 8
  br label %47

47:                                               ; preds = %42, %34
  br label %48

48:                                               ; preds = %47
  %49 = load i64, i64* %6, align 8
  %50 = add i64 %49, 1
  store i64 %50, i64* %6, align 8
  br label %28

51:                                               ; preds = %28
  %52 = load %struct.Frame*, %struct.Frame** %5, align 8
  %53 = getelementptr inbounds %struct.Frame, %struct.Frame* %52, i32 0, i32 2
  %54 = load %struct.Frame*, %struct.Frame** %53, align 8
  store %struct.Frame* %54, %struct.Frame** %5, align 8
  br label %24

55:                                               ; preds = %24
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 11), align 8
  %56 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %57 = call i32 @ReleaseMutex(i8* %56)
  store i64 1, i64* %8, align 8
  %58 = load i64, i64* %8, align 8
  %59 = atomicrmw add i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), i64 %58 seq_cst
  %60 = add i64 %59, %58
  store i64 %60, i64* %9, align 8
  %61 = load i64, i64* %9, align 8
  %62 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  %63 = call i32 @WaitForSingleObject(i8* %62, i32 -1)
  store i64 1, i64* %10, align 8
  %64 = load i64, i64* %10, align 8
  %65 = atomicrmw sub i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), i64 %64 seq_cst
  %66 = sub i64 %65, %64
  store i64 %66, i64* %11, align 8
  %67 = load i64, i64* %11, align 8
  br label %68

68:                                               ; preds = %55, %16
  %69 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  store %struct.ObjectHeader* %69, %struct.ObjectHeader** %3, align 8
  br label %70

70:                                               ; preds = %68, %14
  %71 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  ret %struct.ObjectHeader* %71
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_begin_thread_helper(i8* %0) #1 {
  %2 = alloca i8*, align 8
  %3 = alloca %struct.ThreadStartInfo, align 8
  %4 = alloca %struct.Frame, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  store i8* %0, i8** %2, align 8
  %7 = load i8*, i8** %2, align 8
  %8 = bitcast i8* %7 to %struct.ThreadStartInfo*
  %9 = bitcast %struct.ThreadStartInfo* %3 to i8*
  %10 = bitcast %struct.ThreadStartInfo* %8 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 8 %9, i8* align 8 %10, i64 16, i1 false)
  %11 = load i8*, i8** %2, align 8
  call void @free(i8* %11)
  %12 = bitcast %struct.Frame* %4 to i8*
  call void @llvm.memset.p0i8.i64(i8* align 8 %12, i8 0, i64 24, i1 false)
  %13 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 0
  %14 = load i64 (i8*, i8*)*, i64 (i8*, i8*)** %13, align 8
  %15 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 1
  %16 = load i8*, i8** %15, align 8
  %17 = bitcast %struct.Frame* %4 to i8*
  %18 = call i64 %14(i8* %17, i8* %16)
  store i64 1, i64* %5, align 8
  %19 = load i64, i64* %5, align 8
  %20 = atomicrmw sub i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), i64 %19 seq_cst
  %21 = sub i64 %20, %19
  store i64 %21, i64* %6, align 8
  %22 = load i64, i64* %6, align 8
  ret void
}

declare dso_local void @free(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_new_thread(i64 (i8*, i8*)* %0, i8* %1) #1 {
  %3 = alloca i8*, align 8
  %4 = alloca i64 (i8*, i8*)*, align 8
  %5 = alloca %struct.ThreadStartInfo*, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  store i8* %1, i8** %3, align 8
  store i64 (i8*, i8*)* %0, i64 (i8*, i8*)** %4, align 8
  %8 = call noalias i8* @malloc(i64 16)
  %9 = bitcast i8* %8 to %struct.ThreadStartInfo*
  store %struct.ThreadStartInfo* %9, %struct.ThreadStartInfo** %5, align 8
  %10 = load i64 (i8*, i8*)*, i64 (i8*, i8*)** %4, align 8
  %11 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %5, align 8
  %12 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %11, i32 0, i32 0
  store i64 (i8*, i8*)* %10, i64 (i8*, i8*)** %12, align 8
  %13 = load i8*, i8** %3, align 8
  %14 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %5, align 8
  %15 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %14, i32 0, i32 1
  store i8* %13, i8** %15, align 8
  store i64 1, i64* %6, align 8
  %16 = load i64, i64* %6, align 8
  %17 = atomicrmw add i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), i64 %16 seq_cst
  %18 = add i64 %17, %16
  store i64 %18, i64* %7, align 8
  %19 = load i64, i64* %7, align 8
  %20 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %5, align 8
  %21 = bitcast %struct.ThreadStartInfo* %20 to i8*
  %22 = call i64 @_beginthread(void (i8*)* @SWERVE_begin_thread_helper, i32 0, i8* %21)
  ret void
}

declare dso_local noalias i8* @malloc(i64) #2

declare dso_local i64 @_beginthread(void (i8*)*, i32, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_main() #1 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.ObjectHeader*, align 8
  store i32 0, i32* %1, align 4
  br label %3

3:                                                ; preds = %0, %46
  %4 = call i32 @SwitchToThread()
  %5 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 8
  %6 = icmp eq i64 %5, 0
  br i1 %6, label %7, label %8

7:                                                ; preds = %3
  ret void

8:                                                ; preds = %3
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), align 8
  %9 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  %10 = call i32 @ResetEvent(i8* %9)
  store i8 1, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  br label %11

11:                                               ; preds = %8, %17
  %12 = call i32 @SwitchToThread()
  %13 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 8
  %14 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), align 8
  %15 = icmp eq i64 %13, %14
  br i1 %15, label %16, label %17

16:                                               ; preds = %11
  br label %18

17:                                               ; preds = %11
  br label %11

18:                                               ; preds = %16
  store i8 1, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 11), align 8
  br label %19

19:                                               ; preds = %22, %18
  %20 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  %21 = icmp ne %struct.ObjectHeader* %20, null
  br i1 %21, label %22, label %32

22:                                               ; preds = %19
  %23 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  store %struct.ObjectHeader* %23, %struct.ObjectHeader** %2, align 8
  %24 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %25 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %24, i32 0, i32 1
  %26 = load %struct.ObjectHeader*, %struct.ObjectHeader** %25, align 8
  store %struct.ObjectHeader* %26, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  %27 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %28 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %27, i32 0, i32 2
  %29 = load void (i8*)*, void (i8*)** %28, align 8
  %30 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %31 = bitcast %struct.ObjectHeader* %30 to i8*
  call void %29(i8* %31)
  br label %19

32:                                               ; preds = %19
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 11), align 8
  %33 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  call void @free(i8* %33)
  %34 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  store i8* %34, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %35 = call noalias i8* @malloc(i64 1024)
  store i8* %35, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  %36 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  call void @llvm.memset.p0i8.i64(i8* align 1 %36, i8 34, i64 1024, i1 false)
  %37 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), align 8
  store i64 %37, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  %38 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  %39 = call i32 @SetEvent(i8* %38)
  br label %40

40:                                               ; preds = %32, %45
  %41 = call i32 @SwitchToThread()
  %42 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), align 8
  %43 = icmp eq i64 %42, 0
  br i1 %43, label %44, label %45

44:                                               ; preds = %40
  br label %46

45:                                               ; preds = %40
  br label %40

46:                                               ; preds = %44
  br label %3
}

declare dllimport i32 @SwitchToThread() #2

declare dllimport i32 @ResetEvent(i8*) #2

declare dllimport i32 @SetEvent(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_init() #1 {
  %1 = call i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES* null, i32 0, i8* null)
  store i8* %1, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %2 = call i8* @CreateEventA(%struct._SECURITY_ATTRIBUTES* null, i32 1, i32 1, i8* null)
  store i8* %2, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 8
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), align 8
  store i64 1024, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %3 = call noalias i8* @malloc(i64 1024)
  store i8* %3, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %4 = call noalias i8* @malloc(i64 1024)
  store i8* %4, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), align 8
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 11), align 8
  ret void
}

declare dllimport i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES*, i32, i8*) #2

declare dllimport i8* @CreateEventA(%struct._SECURITY_ATTRIBUTES*, i32, i32, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_display(i8* %0) #1 {
  %2 = alloca i8*, align 8
  store i8* %0, i8** %2, align 8
  %3 = load i8*, i8** %2, align 8
  %4 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @"??_C@_03OFAPEBGM@?$CFs?6?$AA@", i64 0, i64 0), i8* %3)
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_display_pointer(i8* %0, i8* %1) #1 {
  %3 = alloca i8*, align 8
  %4 = alloca i8*, align 8
  store i8* %1, i8** %3, align 8
  store i8* %0, i8** %4, align 8
  %5 = load i8*, i8** %3, align 8
  %6 = load i8*, i8** %4, align 8
  %7 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([7 x i8], [7 x i8]* @"??_C@_06IKJDLJAH@?$CFs?5?$CFp?6?$AA@", i64 0, i64 0), i8* %6, i8* %5)
  ret void
}

; Function Attrs: nounwind
declare void @llvm.va_start(i8*) #5

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vsprintf_l(i8* %0, i8* %1, %struct.__crt_locale_pointers* %2, i8* %3) #1 comdat {
  %5 = alloca i8*, align 8
  %6 = alloca %struct.__crt_locale_pointers*, align 8
  %7 = alloca i8*, align 8
  %8 = alloca i8*, align 8
  store i8* %3, i8** %5, align 8
  store %struct.__crt_locale_pointers* %2, %struct.__crt_locale_pointers** %6, align 8
  store i8* %1, i8** %7, align 8
  store i8* %0, i8** %8, align 8
  %9 = load i8*, i8** %5, align 8
  %10 = load %struct.__crt_locale_pointers*, %struct.__crt_locale_pointers** %6, align 8
  %11 = load i8*, i8** %7, align 8
  %12 = load i8*, i8** %8, align 8
  %13 = call i32 @_vsnprintf_l(i8* %12, i64 -1, i8* %11, %struct.__crt_locale_pointers* %10, i8* %9)
  ret i32 %13
}

; Function Attrs: nounwind
declare void @llvm.va_end(i8*) #5

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vsnprintf_l(i8* %0, i64 %1, i8* %2, %struct.__crt_locale_pointers* %3, i8* %4) #1 comdat {
  %6 = alloca i8*, align 8
  %7 = alloca %struct.__crt_locale_pointers*, align 8
  %8 = alloca i8*, align 8
  %9 = alloca i64, align 8
  %10 = alloca i8*, align 8
  %11 = alloca i32, align 4
  store i8* %4, i8** %6, align 8
  store %struct.__crt_locale_pointers* %3, %struct.__crt_locale_pointers** %7, align 8
  store i8* %2, i8** %8, align 8
  store i64 %1, i64* %9, align 8
  store i8* %0, i8** %10, align 8
  %12 = load i8*, i8** %6, align 8
  %13 = load %struct.__crt_locale_pointers*, %struct.__crt_locale_pointers** %7, align 8
  %14 = load i8*, i8** %8, align 8
  %15 = load i64, i64* %9, align 8
  %16 = load i8*, i8** %10, align 8
  %17 = call i64* @__local_stdio_printf_options()
  %18 = load i64, i64* %17, align 8
  %19 = or i64 %18, 1
  %20 = call i32 @__stdio_common_vsprintf(i64 %19, i8* %16, i64 %15, i8* %14, %struct.__crt_locale_pointers* %13, i8* %12)
  store i32 %20, i32* %11, align 4
  %21 = load i32, i32* %11, align 4
  %22 = icmp slt i32 %21, 0
  br i1 %22, label %23, label %24

23:                                               ; preds = %5
  br label %26

24:                                               ; preds = %5
  %25 = load i32, i32* %11, align 4
  br label %26

26:                                               ; preds = %24, %23
  %27 = phi i32 [ -1, %23 ], [ %25, %24 ]
  ret i32 %27
}

declare dso_local i32 @__stdio_common_vsprintf(i64, i8*, i64, i8*, %struct.__crt_locale_pointers*, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i64* @__local_stdio_printf_options() #1 comdat {
  ret i64* @__local_stdio_printf_options._OptionsStorage
}

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vfprintf_l(%struct._iobuf* %0, i8* %1, %struct.__crt_locale_pointers* %2, i8* %3) #1 comdat {
  %5 = alloca i8*, align 8
  %6 = alloca %struct.__crt_locale_pointers*, align 8
  %7 = alloca i8*, align 8
  %8 = alloca %struct._iobuf*, align 8
  store i8* %3, i8** %5, align 8
  store %struct.__crt_locale_pointers* %2, %struct.__crt_locale_pointers** %6, align 8
  store i8* %1, i8** %7, align 8
  store %struct._iobuf* %0, %struct._iobuf** %8, align 8
  %9 = load i8*, i8** %5, align 8
  %10 = load %struct.__crt_locale_pointers*, %struct.__crt_locale_pointers** %6, align 8
  %11 = load i8*, i8** %7, align 8
  %12 = load %struct._iobuf*, %struct._iobuf** %8, align 8
  %13 = call i64* @__local_stdio_printf_options()
  %14 = load i64, i64* %13, align 8
  %15 = call i32 @__stdio_common_vfprintf(i64 %14, %struct._iobuf* %12, i8* %11, %struct.__crt_locale_pointers* %10, i8* %9)
  ret i32 %15
}

declare dso_local %struct._iobuf* @__acrt_iob_func(i32) #2

declare dso_local i32 @__stdio_common_vfprintf(i64, %struct._iobuf*, i8*, %struct.__crt_locale_pointers*, i8*) #2

attributes #0 = { nobuiltin noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="none" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="none" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="none" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { argmemonly nounwind willreturn writeonly }
attributes #4 = { argmemonly nounwind willreturn }
attributes #5 = { nounwind }

!llvm.linker.options = !{!0, !0}
!llvm.module.flags = !{!1, !2}
!llvm.ident = !{!3}

!0 = !{!"/DEFAULTLIB:uuid.lib"}
!1 = !{i32 1, !"wchar_size", i32 2}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{!"clang version 11.1.0"}
