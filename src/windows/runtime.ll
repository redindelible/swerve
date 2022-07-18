; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.__crt_locale_pointers = type { %struct.__crt_locale_data*, %struct.__crt_multibyte_data* }
%struct.__crt_locale_data = type opaque
%struct.__crt_multibyte_data = type opaque
%struct.GCState = type { i8*, i8*, i8, i64, i64, %struct.ObjectHeader*, i8*, i8*, i64, i64, i64 }
%struct.ObjectHeader = type { i64, %struct.ObjectHeader*, void (%struct.GCState*, i8*)* }
%struct.Frame = type { i64, %struct.Frame*, [0 x %struct.ObjectHeader**] }
%struct.ThreadStartInfo = type { %struct.GCState*, i64 (i8*, i8*)*, i8* }
%struct._iobuf = type { i8* }
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

$"??_C@_0DD@NBDMBMMC@Completed?5collection?3?5freed?5?$CFlli@" = comdat any

@"??_C@_0DD@NBDMBMMC@Completed?5collection?3?5freed?5?$CFlli@" = linkonce_odr dso_local unnamed_addr constant [51 x i8] c"Completed collection: freed %lli bytes of memory.\0A\00", comdat, align 1
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
define dso_local i8* @SWERVE_gc_allocate(%struct.GCState* %0, i64 %1, void (%struct.GCState*, i8*)* %2) #1 {
  %4 = alloca void (%struct.GCState*, i8*)*, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.GCState*, align 8
  %7 = alloca %struct.ObjectHeader*, align 8
  store void (%struct.GCState*, i8*)* %2, void (%struct.GCState*, i8*)** %4, align 8
  store i64 %1, i64* %5, align 8
  store %struct.GCState* %0, %struct.GCState** %6, align 8
  %8 = load %struct.GCState*, %struct.GCState** %6, align 8
  %9 = getelementptr inbounds %struct.GCState, %struct.GCState* %8, i32 0, i32 0
  %10 = load i8*, i8** %9, align 8
  %11 = call i32 @WaitForSingleObject(i8* %10, i32 -1)
  %12 = load %struct.GCState*, %struct.GCState** %6, align 8
  %13 = getelementptr inbounds %struct.GCState, %struct.GCState* %12, i32 0, i32 6
  %14 = load i8*, i8** %13, align 8
  %15 = load %struct.GCState*, %struct.GCState** %6, align 8
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 9
  %17 = load i64, i64* %16, align 8
  %18 = getelementptr i8, i8* %14, i64 %17
  %19 = bitcast i8* %18 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %19, %struct.ObjectHeader** %7, align 8
  %20 = load i64, i64* %5, align 8
  %21 = load %struct.GCState*, %struct.GCState** %6, align 8
  %22 = getelementptr inbounds %struct.GCState, %struct.GCState* %21, i32 0, i32 9
  %23 = load i64, i64* %22, align 8
  %24 = add i64 %23, %20
  store i64 %24, i64* %22, align 8
  %25 = load i64, i64* %5, align 8
  %26 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %27 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %26, i32 0, i32 0
  store i64 %25, i64* %27, align 8
  %28 = load void (%struct.GCState*, i8*)*, void (%struct.GCState*, i8*)** %4, align 8
  %29 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %30 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %29, i32 0, i32 2
  store void (%struct.GCState*, i8*)* %28, void (%struct.GCState*, i8*)** %30, align 8
  %31 = load %struct.GCState*, %struct.GCState** %6, align 8
  %32 = getelementptr inbounds %struct.GCState, %struct.GCState* %31, i32 0, i32 0
  %33 = load i8*, i8** %32, align 8
  %34 = call i32 @ReleaseMutex(i8* %33)
  %35 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %36 = bitcast %struct.ObjectHeader* %35 to i8*
  ret i8* %36
}

declare dllimport i32 @WaitForSingleObject(i8*, i32) #2

declare dllimport i32 @ReleaseMutex(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_move(%struct.GCState* %0, %struct.ObjectHeader** %1) #1 {
  %3 = alloca %struct.ObjectHeader**, align 8
  %4 = alloca %struct.GCState*, align 8
  %5 = alloca %struct.ObjectHeader*, align 8
  %6 = alloca i64, align 8
  %7 = alloca %struct.ObjectHeader*, align 8
  store %struct.ObjectHeader** %1, %struct.ObjectHeader*** %3, align 8
  store %struct.GCState* %0, %struct.GCState** %4, align 8
  %8 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %3, align 8
  %9 = icmp eq %struct.ObjectHeader** %8, null
  br i1 %9, label %10, label %11

10:                                               ; preds = %2
  br label %78

11:                                               ; preds = %2
  %12 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %3, align 8
  %13 = load %struct.ObjectHeader*, %struct.ObjectHeader** %12, align 8
  store %struct.ObjectHeader* %13, %struct.ObjectHeader** %5, align 8
  %14 = load %struct.GCState*, %struct.GCState** %4, align 8
  %15 = getelementptr inbounds %struct.GCState, %struct.GCState* %14, i32 0, i32 6
  %16 = load i8*, i8** %15, align 8
  %17 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %18 = bitcast %struct.ObjectHeader* %17 to i8*
  %19 = icmp ule i8* %16, %18
  br i1 %19, label %20, label %78

20:                                               ; preds = %11
  %21 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %22 = load %struct.GCState*, %struct.GCState** %4, align 8
  %23 = getelementptr inbounds %struct.GCState, %struct.GCState* %22, i32 0, i32 6
  %24 = load i8*, i8** %23, align 8
  %25 = load %struct.GCState*, %struct.GCState** %4, align 8
  %26 = getelementptr inbounds %struct.GCState, %struct.GCState* %25, i32 0, i32 8
  %27 = load i64, i64* %26, align 8
  %28 = getelementptr i8, i8* %24, i64 %27
  %29 = bitcast i8* %28 to %struct.ObjectHeader*
  %30 = icmp ult %struct.ObjectHeader* %21, %29
  br i1 %30, label %31, label %78

31:                                               ; preds = %20
  %32 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %33 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %32, i32 0, i32 0
  %34 = load i64, i64* %33, align 8
  %35 = icmp eq i64 %34, 0
  br i1 %35, label %36, label %41

36:                                               ; preds = %31
  %37 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %38 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %37, i32 0, i32 1
  %39 = load %struct.ObjectHeader*, %struct.ObjectHeader** %38, align 8
  %40 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %3, align 8
  store %struct.ObjectHeader* %39, %struct.ObjectHeader** %40, align 8
  br label %78

41:                                               ; preds = %31
  %42 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %43 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %42, i32 0, i32 0
  %44 = load i64, i64* %43, align 8
  store i64 %44, i64* %6, align 8
  %45 = load %struct.GCState*, %struct.GCState** %4, align 8
  %46 = getelementptr inbounds %struct.GCState, %struct.GCState* %45, i32 0, i32 7
  %47 = load i8*, i8** %46, align 8
  %48 = load %struct.GCState*, %struct.GCState** %4, align 8
  %49 = getelementptr inbounds %struct.GCState, %struct.GCState* %48, i32 0, i32 10
  %50 = load i64, i64* %49, align 8
  %51 = getelementptr i8, i8* %47, i64 %50
  %52 = bitcast i8* %51 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %52, %struct.ObjectHeader** %7, align 8
  %53 = load i64, i64* %6, align 8
  %54 = load %struct.GCState*, %struct.GCState** %4, align 8
  %55 = getelementptr inbounds %struct.GCState, %struct.GCState* %54, i32 0, i32 10
  %56 = load i64, i64* %55, align 8
  %57 = add i64 %56, %53
  store i64 %57, i64* %55, align 8
  %58 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %59 = bitcast %struct.ObjectHeader* %58 to i8*
  %60 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %61 = bitcast %struct.ObjectHeader* %60 to i8*
  %62 = load i64, i64* %6, align 8
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 8 %59, i8* align 8 %61, i64 %62, i1 false)
  %63 = load %struct.GCState*, %struct.GCState** %4, align 8
  %64 = getelementptr inbounds %struct.GCState, %struct.GCState* %63, i32 0, i32 5
  %65 = load %struct.ObjectHeader*, %struct.ObjectHeader** %64, align 8
  %66 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %67 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %66, i32 0, i32 1
  store %struct.ObjectHeader* %65, %struct.ObjectHeader** %67, align 8
  %68 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %69 = load %struct.GCState*, %struct.GCState** %4, align 8
  %70 = getelementptr inbounds %struct.GCState, %struct.GCState* %69, i32 0, i32 5
  store %struct.ObjectHeader* %68, %struct.ObjectHeader** %70, align 8
  %71 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %72 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %71, i32 0, i32 0
  store i64 0, i64* %72, align 8
  %73 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %74 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %75 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %74, i32 0, i32 1
  store %struct.ObjectHeader* %73, %struct.ObjectHeader** %75, align 8
  %76 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %77 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %3, align 8
  store %struct.ObjectHeader* %76, %struct.ObjectHeader** %77, align 8
  br label %78

78:                                               ; preds = %10, %36, %41, %20, %11
  ret void
}

; Function Attrs: argmemonly nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_check(%struct.Frame* %0, %struct.GCState* %1) #1 {
  %3 = alloca %struct.GCState*, align 8
  %4 = alloca %struct.Frame*, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  store %struct.GCState* %1, %struct.GCState** %3, align 8
  store %struct.Frame* %0, %struct.Frame** %4, align 8
  %10 = load %struct.GCState*, %struct.GCState** %3, align 8
  %11 = getelementptr inbounds %struct.GCState, %struct.GCState* %10, i32 0, i32 2
  %12 = load i8, i8* %11, align 8
  %13 = trunc i8 %12 to i1
  br i1 %13, label %14, label %64

14:                                               ; preds = %2
  %15 = load %struct.GCState*, %struct.GCState** %3, align 8
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 0
  %17 = load i8*, i8** %16, align 8
  %18 = call i32 @WaitForSingleObject(i8* %17, i32 -1)
  br label %19

19:                                               ; preds = %39, %14
  %20 = load %struct.Frame*, %struct.Frame** %4, align 8
  %21 = icmp ne %struct.Frame* %20, null
  br i1 %21, label %22, label %43

22:                                               ; preds = %19
  store i64 0, i64* %5, align 8
  br label %23

23:                                               ; preds = %36, %22
  %24 = load i64, i64* %5, align 8
  %25 = load %struct.Frame*, %struct.Frame** %4, align 8
  %26 = getelementptr inbounds %struct.Frame, %struct.Frame* %25, i32 0, i32 0
  %27 = load i64, i64* %26, align 8
  %28 = icmp ult i64 %24, %27
  br i1 %28, label %29, label %39

29:                                               ; preds = %23
  %30 = load %struct.Frame*, %struct.Frame** %4, align 8
  %31 = getelementptr inbounds %struct.Frame, %struct.Frame* %30, i32 0, i32 2
  %32 = load i64, i64* %5, align 8
  %33 = getelementptr inbounds [0 x %struct.ObjectHeader**], [0 x %struct.ObjectHeader**]* %31, i64 0, i64 %32
  %34 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %33, align 8
  %35 = load %struct.GCState*, %struct.GCState** %3, align 8
  call void @SWERVE_gc_move(%struct.GCState* %35, %struct.ObjectHeader** %34)
  br label %36

36:                                               ; preds = %29
  %37 = load i64, i64* %5, align 8
  %38 = add i64 %37, 1
  store i64 %38, i64* %5, align 8
  br label %23

39:                                               ; preds = %23
  %40 = load %struct.Frame*, %struct.Frame** %4, align 8
  %41 = getelementptr inbounds %struct.Frame, %struct.Frame* %40, i32 0, i32 1
  %42 = load %struct.Frame*, %struct.Frame** %41, align 8
  store %struct.Frame* %42, %struct.Frame** %4, align 8
  br label %19

43:                                               ; preds = %19
  %44 = load %struct.GCState*, %struct.GCState** %3, align 8
  %45 = getelementptr inbounds %struct.GCState, %struct.GCState* %44, i32 0, i32 0
  %46 = load i8*, i8** %45, align 8
  %47 = call i32 @ReleaseMutex(i8* %46)
  %48 = load %struct.GCState*, %struct.GCState** %3, align 8
  %49 = getelementptr inbounds %struct.GCState, %struct.GCState* %48, i32 0, i32 4
  store i64 1, i64* %6, align 8
  %50 = load i64, i64* %6, align 8
  %51 = atomicrmw add i64* %49, i64 %50 seq_cst
  %52 = add i64 %51, %50
  store i64 %52, i64* %7, align 8
  %53 = load i64, i64* %7, align 8
  %54 = load %struct.GCState*, %struct.GCState** %3, align 8
  %55 = getelementptr inbounds %struct.GCState, %struct.GCState* %54, i32 0, i32 1
  %56 = load i8*, i8** %55, align 8
  %57 = call i32 @WaitForSingleObject(i8* %56, i32 -1)
  %58 = load %struct.GCState*, %struct.GCState** %3, align 8
  %59 = getelementptr inbounds %struct.GCState, %struct.GCState* %58, i32 0, i32 4
  store i64 1, i64* %8, align 8
  %60 = load i64, i64* %8, align 8
  %61 = atomicrmw sub i64* %59, i64 %60 seq_cst
  %62 = sub i64 %61, %60
  store i64 %62, i64* %9, align 8
  %63 = load i64, i64* %9, align 8
  br label %64

64:                                               ; preds = %43, %2
  ret void
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
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 8 %9, i8* align 8 %10, i64 24, i1 false)
  %11 = load i8*, i8** %2, align 8
  call void @free(i8* %11)
  %12 = bitcast %struct.Frame* %4 to i8*
  call void @llvm.memset.p0i8.i64(i8* align 8 %12, i8 0, i64 16, i1 false)
  %13 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 1
  %14 = load i64 (i8*, i8*)*, i64 (i8*, i8*)** %13, align 8
  %15 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 2
  %16 = load i8*, i8** %15, align 8
  %17 = bitcast %struct.Frame* %4 to i8*
  %18 = call i64 %14(i8* %17, i8* %16)
  %19 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 0
  %20 = load %struct.GCState*, %struct.GCState** %19, align 8
  %21 = getelementptr inbounds %struct.GCState, %struct.GCState* %20, i32 0, i32 3
  store i64 1, i64* %5, align 8
  %22 = load i64, i64* %5, align 8
  %23 = atomicrmw sub i64* %21, i64 %22 seq_cst
  %24 = sub i64 %23, %22
  store i64 %24, i64* %6, align 8
  %25 = load i64, i64* %6, align 8
  ret void
}

declare dso_local void @free(i8*) #2

; Function Attrs: argmemonly nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #4

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_new_thread(%struct.GCState* %0, i64 (i8*, i8*)* %1, i8* %2) #1 {
  %4 = alloca i8*, align 8
  %5 = alloca i64 (i8*, i8*)*, align 8
  %6 = alloca %struct.GCState*, align 8
  %7 = alloca %struct.ThreadStartInfo*, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  store i8* %2, i8** %4, align 8
  store i64 (i8*, i8*)* %1, i64 (i8*, i8*)** %5, align 8
  store %struct.GCState* %0, %struct.GCState** %6, align 8
  %10 = call noalias i8* @malloc(i64 24)
  %11 = bitcast i8* %10 to %struct.ThreadStartInfo*
  store %struct.ThreadStartInfo* %11, %struct.ThreadStartInfo** %7, align 8
  %12 = load %struct.GCState*, %struct.GCState** %6, align 8
  %13 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %7, align 8
  %14 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %13, i32 0, i32 0
  store %struct.GCState* %12, %struct.GCState** %14, align 8
  %15 = load i64 (i8*, i8*)*, i64 (i8*, i8*)** %5, align 8
  %16 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %7, align 8
  %17 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %16, i32 0, i32 1
  store i64 (i8*, i8*)* %15, i64 (i8*, i8*)** %17, align 8
  %18 = load i8*, i8** %4, align 8
  %19 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %7, align 8
  %20 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %19, i32 0, i32 2
  store i8* %18, i8** %20, align 8
  %21 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %7, align 8
  %22 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %21, i32 0, i32 0
  %23 = load %struct.GCState*, %struct.GCState** %22, align 8
  %24 = getelementptr inbounds %struct.GCState, %struct.GCState* %23, i32 0, i32 3
  store i64 1, i64* %8, align 8
  %25 = load i64, i64* %8, align 8
  %26 = atomicrmw add i64* %24, i64 %25 seq_cst
  %27 = add i64 %26, %25
  store i64 %27, i64* %9, align 8
  %28 = load i64, i64* %9, align 8
  %29 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %7, align 8
  %30 = bitcast %struct.ThreadStartInfo* %29 to i8*
  %31 = call i64 @_beginthread(void (i8*)* @SWERVE_begin_thread_helper, i32 0, i8* %30)
  ret void
}

declare dso_local noalias i8* @malloc(i64) #2

declare dso_local i64 @_beginthread(void (i8*)*, i32, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_main(%struct.GCState* %0) #1 {
  %2 = alloca %struct.GCState*, align 8
  %3 = alloca i32, align 4
  %4 = alloca %struct.ObjectHeader*, align 8
  store %struct.GCState* %0, %struct.GCState** %2, align 8
  store i32 0, i32* %3, align 4
  br label %5

5:                                                ; preds = %1, %97
  %6 = call i32 @SwitchToThread()
  %7 = load %struct.GCState*, %struct.GCState** %2, align 8
  %8 = getelementptr inbounds %struct.GCState, %struct.GCState* %7, i32 0, i32 3
  %9 = load i64, i64* %8, align 8
  %10 = icmp eq i64 %9, 0
  br i1 %10, label %11, label %12

11:                                               ; preds = %5
  ret void

12:                                               ; preds = %5
  %13 = load %struct.GCState*, %struct.GCState** %2, align 8
  %14 = getelementptr inbounds %struct.GCState, %struct.GCState* %13, i32 0, i32 5
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %14, align 8
  %15 = load %struct.GCState*, %struct.GCState** %2, align 8
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 10
  store i64 0, i64* %16, align 8
  %17 = load %struct.GCState*, %struct.GCState** %2, align 8
  %18 = getelementptr inbounds %struct.GCState, %struct.GCState* %17, i32 0, i32 1
  %19 = load i8*, i8** %18, align 8
  %20 = call i32 @ResetEvent(i8* %19)
  %21 = load %struct.GCState*, %struct.GCState** %2, align 8
  %22 = getelementptr inbounds %struct.GCState, %struct.GCState* %21, i32 0, i32 2
  store i8 1, i8* %22, align 8
  br label %23

23:                                               ; preds = %12, %33
  %24 = call i32 @SwitchToThread()
  %25 = load %struct.GCState*, %struct.GCState** %2, align 8
  %26 = getelementptr inbounds %struct.GCState, %struct.GCState* %25, i32 0, i32 3
  %27 = load i64, i64* %26, align 8
  %28 = load %struct.GCState*, %struct.GCState** %2, align 8
  %29 = getelementptr inbounds %struct.GCState, %struct.GCState* %28, i32 0, i32 4
  %30 = load i64, i64* %29, align 8
  %31 = icmp eq i64 %27, %30
  br i1 %31, label %32, label %33

32:                                               ; preds = %23
  br label %34

33:                                               ; preds = %23
  br label %23

34:                                               ; preds = %32
  br label %35

35:                                               ; preds = %40, %34
  %36 = load %struct.GCState*, %struct.GCState** %2, align 8
  %37 = getelementptr inbounds %struct.GCState, %struct.GCState* %36, i32 0, i32 5
  %38 = load %struct.ObjectHeader*, %struct.ObjectHeader** %37, align 8
  %39 = icmp ne %struct.ObjectHeader* %38, null
  br i1 %39, label %40, label %55

40:                                               ; preds = %35
  %41 = load %struct.GCState*, %struct.GCState** %2, align 8
  %42 = getelementptr inbounds %struct.GCState, %struct.GCState* %41, i32 0, i32 5
  %43 = load %struct.ObjectHeader*, %struct.ObjectHeader** %42, align 8
  store %struct.ObjectHeader* %43, %struct.ObjectHeader** %4, align 8
  %44 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %45 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %44, i32 0, i32 1
  %46 = load %struct.ObjectHeader*, %struct.ObjectHeader** %45, align 8
  %47 = load %struct.GCState*, %struct.GCState** %2, align 8
  %48 = getelementptr inbounds %struct.GCState, %struct.GCState* %47, i32 0, i32 5
  store %struct.ObjectHeader* %46, %struct.ObjectHeader** %48, align 8
  %49 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %50 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %49, i32 0, i32 2
  %51 = load void (%struct.GCState*, i8*)*, void (%struct.GCState*, i8*)** %50, align 8
  %52 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %53 = bitcast %struct.ObjectHeader* %52 to i8*
  %54 = load %struct.GCState*, %struct.GCState** %2, align 8
  call void %51(%struct.GCState* %54, i8* %53)
  br label %35

55:                                               ; preds = %35
  %56 = load %struct.GCState*, %struct.GCState** %2, align 8
  %57 = getelementptr inbounds %struct.GCState, %struct.GCState* %56, i32 0, i32 6
  %58 = load i8*, i8** %57, align 8
  call void @free(i8* %58)
  %59 = load %struct.GCState*, %struct.GCState** %2, align 8
  %60 = getelementptr inbounds %struct.GCState, %struct.GCState* %59, i32 0, i32 7
  %61 = load i8*, i8** %60, align 8
  %62 = load %struct.GCState*, %struct.GCState** %2, align 8
  %63 = getelementptr inbounds %struct.GCState, %struct.GCState* %62, i32 0, i32 6
  store i8* %61, i8** %63, align 8
  %64 = call noalias i8* @malloc(i64 1024)
  %65 = load %struct.GCState*, %struct.GCState** %2, align 8
  %66 = getelementptr inbounds %struct.GCState, %struct.GCState* %65, i32 0, i32 7
  store i8* %64, i8** %66, align 8
  %67 = load %struct.GCState*, %struct.GCState** %2, align 8
  %68 = getelementptr inbounds %struct.GCState, %struct.GCState* %67, i32 0, i32 7
  %69 = load i8*, i8** %68, align 8
  call void @llvm.memset.p0i8.i64(i8* align 1 %69, i8 34, i64 1024, i1 false)
  %70 = load %struct.GCState*, %struct.GCState** %2, align 8
  %71 = getelementptr inbounds %struct.GCState, %struct.GCState* %70, i32 0, i32 9
  %72 = load i64, i64* %71, align 8
  %73 = load %struct.GCState*, %struct.GCState** %2, align 8
  %74 = getelementptr inbounds %struct.GCState, %struct.GCState* %73, i32 0, i32 10
  %75 = load i64, i64* %74, align 8
  %76 = sub i64 %72, %75
  %77 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([51 x i8], [51 x i8]* @"??_C@_0DD@NBDMBMMC@Completed?5collection?3?5freed?5?$CFlli@", i64 0, i64 0), i64 %76)
  %78 = load %struct.GCState*, %struct.GCState** %2, align 8
  %79 = getelementptr inbounds %struct.GCState, %struct.GCState* %78, i32 0, i32 10
  %80 = load i64, i64* %79, align 8
  %81 = load %struct.GCState*, %struct.GCState** %2, align 8
  %82 = getelementptr inbounds %struct.GCState, %struct.GCState* %81, i32 0, i32 9
  store i64 %80, i64* %82, align 8
  %83 = load %struct.GCState*, %struct.GCState** %2, align 8
  %84 = getelementptr inbounds %struct.GCState, %struct.GCState* %83, i32 0, i32 2
  store i8 0, i8* %84, align 8
  %85 = load %struct.GCState*, %struct.GCState** %2, align 8
  %86 = getelementptr inbounds %struct.GCState, %struct.GCState* %85, i32 0, i32 1
  %87 = load i8*, i8** %86, align 8
  %88 = call i32 @SetEvent(i8* %87)
  br label %89

89:                                               ; preds = %55, %96
  %90 = call i32 @SwitchToThread()
  %91 = load %struct.GCState*, %struct.GCState** %2, align 8
  %92 = getelementptr inbounds %struct.GCState, %struct.GCState* %91, i32 0, i32 4
  %93 = load i64, i64* %92, align 8
  %94 = icmp eq i64 %93, 0
  br i1 %94, label %95, label %96

95:                                               ; preds = %89
  br label %97

96:                                               ; preds = %89
  br label %89

97:                                               ; preds = %95
  br label %5
}

declare dllimport i32 @SwitchToThread() #2

declare dllimport i32 @ResetEvent(i8*) #2

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

declare dllimport i32 @SetEvent(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_init(%struct.GCState* %0) #1 {
  %2 = alloca %struct.GCState*, align 8
  store %struct.GCState* %0, %struct.GCState** %2, align 8
  %3 = call i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES* null, i32 0, i8* null)
  %4 = load %struct.GCState*, %struct.GCState** %2, align 8
  %5 = getelementptr inbounds %struct.GCState, %struct.GCState* %4, i32 0, i32 0
  store i8* %3, i8** %5, align 8
  %6 = call i8* @CreateEventA(%struct._SECURITY_ATTRIBUTES* null, i32 1, i32 1, i8* null)
  %7 = load %struct.GCState*, %struct.GCState** %2, align 8
  %8 = getelementptr inbounds %struct.GCState, %struct.GCState* %7, i32 0, i32 1
  store i8* %6, i8** %8, align 8
  %9 = load %struct.GCState*, %struct.GCState** %2, align 8
  %10 = getelementptr inbounds %struct.GCState, %struct.GCState* %9, i32 0, i32 2
  store i8 0, i8* %10, align 8
  %11 = load %struct.GCState*, %struct.GCState** %2, align 8
  %12 = getelementptr inbounds %struct.GCState, %struct.GCState* %11, i32 0, i32 3
  store i64 0, i64* %12, align 8
  %13 = load %struct.GCState*, %struct.GCState** %2, align 8
  %14 = getelementptr inbounds %struct.GCState, %struct.GCState* %13, i32 0, i32 4
  store i64 0, i64* %14, align 8
  %15 = load %struct.GCState*, %struct.GCState** %2, align 8
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 8
  store i64 1024, i64* %16, align 8
  %17 = call noalias i8* @malloc(i64 1024)
  %18 = load %struct.GCState*, %struct.GCState** %2, align 8
  %19 = getelementptr inbounds %struct.GCState, %struct.GCState* %18, i32 0, i32 6
  store i8* %17, i8** %19, align 8
  %20 = call noalias i8* @malloc(i64 1024)
  %21 = load %struct.GCState*, %struct.GCState** %2, align 8
  %22 = getelementptr inbounds %struct.GCState, %struct.GCState* %21, i32 0, i32 7
  store i8* %20, i8** %22, align 8
  %23 = load %struct.GCState*, %struct.GCState** %2, align 8
  %24 = getelementptr inbounds %struct.GCState, %struct.GCState* %23, i32 0, i32 9
  store i64 0, i64* %24, align 8
  %25 = load %struct.GCState*, %struct.GCState** %2, align 8
  %26 = getelementptr inbounds %struct.GCState, %struct.GCState* %25, i32 0, i32 10
  store i64 0, i64* %26, align 8
  %27 = load %struct.GCState*, %struct.GCState** %2, align 8
  %28 = getelementptr inbounds %struct.GCState, %struct.GCState* %27, i32 0, i32 5
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %28, align 8
  ret void
}

declare dllimport i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES*, i32, i8*) #2

declare dllimport i8* @CreateEventA(%struct._SECURITY_ATTRIBUTES*, i32, i32, i8*) #2

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
attributes #3 = { argmemonly nounwind willreturn }
attributes #4 = { argmemonly nounwind willreturn writeonly }
attributes #5 = { nounwind }

!llvm.linker.options = !{!0, !0}
!llvm.module.flags = !{!1, !2}
!llvm.ident = !{!3}

!0 = !{!"/DEFAULTLIB:uuid.lib"}
!1 = !{i32 1, !"wchar_size", i32 2}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{!"clang version 11.1.0"}
