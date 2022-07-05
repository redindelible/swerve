; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.__crt_locale_pointers = type { %struct.__crt_locale_data*, %struct.__crt_multibyte_data* }
%struct.__crt_locale_data = type opaque
%struct.__crt_multibyte_data = type opaque
%struct.GCState = type { i8*, i8*, i8, i64, i64, i8*, i64, i8*, i64, i64, %struct.ObjectHeader*, %struct.ObjectHeader*, %struct.ObjectHeader* }
%struct.ObjectHeader = type { %struct.ObjectHeader*, i8, void (%struct.GCState*, i8*)* }
%struct.Frame = type { i64, %struct.Frame*, [0 x i8**] }
%struct.ThreadStartInfo = type { %struct.GCState*, i64 (i8*, i8*)*, i8* }
%struct._SECURITY_ATTRIBUTES = type { i32, i8*, i32 }

$sprintf = comdat any

$vsprintf = comdat any

$_snprintf = comdat any

$_vsnprintf = comdat any

$_vsprintf_l = comdat any

$_vsnprintf_l = comdat any

$__local_stdio_printf_options = comdat any

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
  %13 = getelementptr inbounds %struct.GCState, %struct.GCState* %12, i32 0, i32 5
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
  %25 = load %struct.GCState*, %struct.GCState** %6, align 8
  %26 = getelementptr inbounds %struct.GCState, %struct.GCState* %25, i32 0, i32 11
  %27 = load %struct.ObjectHeader*, %struct.ObjectHeader** %26, align 8
  %28 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %29 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %28, i32 0, i32 0
  store %struct.ObjectHeader* %27, %struct.ObjectHeader** %29, align 8
  %30 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %31 = load %struct.GCState*, %struct.GCState** %6, align 8
  %32 = getelementptr inbounds %struct.GCState, %struct.GCState* %31, i32 0, i32 11
  store %struct.ObjectHeader* %30, %struct.ObjectHeader** %32, align 8
  %33 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %34 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %33, i32 0, i32 1
  store i8 1, i8* %34, align 8
  %35 = load void (%struct.GCState*, i8*)*, void (%struct.GCState*, i8*)** %4, align 8
  %36 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %37 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %36, i32 0, i32 2
  store void (%struct.GCState*, i8*)* %35, void (%struct.GCState*, i8*)** %37, align 8
  %38 = load %struct.GCState*, %struct.GCState** %6, align 8
  %39 = getelementptr inbounds %struct.GCState, %struct.GCState* %38, i32 0, i32 0
  %40 = load i8*, i8** %39, align 8
  %41 = call i32 @ReleaseMutex(i8* %40)
  %42 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %43 = bitcast %struct.ObjectHeader* %42 to i8*
  ret i8* %43
}

declare dllimport i32 @WaitForSingleObject(i8*, i32) #2

declare dllimport i32 @ReleaseMutex(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_check(%struct.Frame* %0, %struct.GCState* %1) #1 {
  %3 = alloca %struct.GCState*, align 8
  %4 = alloca %struct.Frame*, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  store %struct.GCState* %1, %struct.GCState** %3, align 8
  store %struct.Frame* %0, %struct.Frame** %4, align 8
  %7 = load %struct.GCState*, %struct.GCState** %3, align 8
  %8 = getelementptr inbounds %struct.GCState, %struct.GCState* %7, i32 0, i32 2
  %9 = load i8, i8* %8, align 8
  %10 = trunc i8 %9 to i1
  br i1 %10, label %11, label %30

11:                                               ; preds = %2
  %12 = load %struct.GCState*, %struct.GCState** %3, align 8
  %13 = getelementptr inbounds %struct.GCState, %struct.GCState* %12, i32 0, i32 0
  %14 = load i8*, i8** %13, align 8
  %15 = call i32 @WaitForSingleObject(i8* %14, i32 -1)
  %16 = load %struct.GCState*, %struct.GCState** %3, align 8
  %17 = getelementptr inbounds %struct.GCState, %struct.GCState* %16, i32 0, i32 0
  %18 = load i8*, i8** %17, align 8
  %19 = call i32 @ReleaseMutex(i8* %18)
  %20 = load %struct.GCState*, %struct.GCState** %3, align 8
  %21 = getelementptr inbounds %struct.GCState, %struct.GCState* %20, i32 0, i32 4
  store i64 1, i64* %5, align 8
  %22 = load i64, i64* %5, align 8
  %23 = atomicrmw add i64* %21, i64 %22 seq_cst
  %24 = add i64 %23, %22
  store i64 %24, i64* %6, align 8
  %25 = load i64, i64* %6, align 8
  %26 = load %struct.GCState*, %struct.GCState** %3, align 8
  %27 = getelementptr inbounds %struct.GCState, %struct.GCState* %26, i32 0, i32 1
  %28 = load i8*, i8** %27, align 8
  %29 = call i32 @WaitForSingleObject(i8* %28, i32 -1)
  br label %30

30:                                               ; preds = %11, %2
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @SWERVE_gc_move(%struct.GCState* %0, %struct.ObjectHeader* %1) #1 {
  %3 = alloca %struct.ObjectHeader*, align 8
  %4 = alloca %struct.GCState*, align 8
  store %struct.ObjectHeader* %1, %struct.ObjectHeader** %3, align 8
  store %struct.GCState* %0, %struct.GCState** %4, align 8
  %5 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  %6 = bitcast %struct.ObjectHeader* %5 to i8*
  ret i8* %6
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

; Function Attrs: argmemonly nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #3

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
  store %struct.GCState* %0, %struct.GCState** %2, align 8
  br label %3

3:                                                ; preds = %1, %28
  %4 = call i32 @SwitchToThread()
  %5 = load %struct.GCState*, %struct.GCState** %2, align 8
  %6 = getelementptr inbounds %struct.GCState, %struct.GCState* %5, i32 0, i32 3
  %7 = load i64, i64* %6, align 8
  %8 = icmp eq i64 %7, 0
  br i1 %8, label %9, label %10

9:                                                ; preds = %3
  ret void

10:                                               ; preds = %3
  %11 = load %struct.GCState*, %struct.GCState** %2, align 8
  %12 = getelementptr inbounds %struct.GCState, %struct.GCState* %11, i32 0, i32 1
  %13 = load i8*, i8** %12, align 8
  %14 = call i32 @ResetEvent(i8* %13)
  %15 = load %struct.GCState*, %struct.GCState** %2, align 8
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 2
  store i8 1, i8* %16, align 8
  br label %17

17:                                               ; preds = %10, %27
  %18 = call i32 @SwitchToThread()
  %19 = load %struct.GCState*, %struct.GCState** %2, align 8
  %20 = getelementptr inbounds %struct.GCState, %struct.GCState* %19, i32 0, i32 3
  %21 = load i64, i64* %20, align 8
  %22 = load %struct.GCState*, %struct.GCState** %2, align 8
  %23 = getelementptr inbounds %struct.GCState, %struct.GCState* %22, i32 0, i32 4
  %24 = load i64, i64* %23, align 8
  %25 = icmp eq i64 %21, %24
  br i1 %25, label %26, label %27

26:                                               ; preds = %17
  br label %28

27:                                               ; preds = %17
  br label %17

28:                                               ; preds = %26
  %29 = load %struct.GCState*, %struct.GCState** %2, align 8
  %30 = getelementptr inbounds %struct.GCState, %struct.GCState* %29, i32 0, i32 4
  store i64 0, i64* %30, align 8
  %31 = load %struct.GCState*, %struct.GCState** %2, align 8
  %32 = getelementptr inbounds %struct.GCState, %struct.GCState* %31, i32 0, i32 2
  store i8 0, i8* %32, align 8
  %33 = load %struct.GCState*, %struct.GCState** %2, align 8
  %34 = getelementptr inbounds %struct.GCState, %struct.GCState* %33, i32 0, i32 1
  %35 = load i8*, i8** %34, align 8
  %36 = call i32 @SetEvent(i8* %35)
  br label %3
}

declare dllimport i32 @SwitchToThread() #2

declare dllimport i32 @ResetEvent(i8*) #2

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
  %15 = call noalias i8* @malloc(i64 1024)
  %16 = load %struct.GCState*, %struct.GCState** %2, align 8
  %17 = getelementptr inbounds %struct.GCState, %struct.GCState* %16, i32 0, i32 5
  store i8* %15, i8** %17, align 8
  %18 = load %struct.GCState*, %struct.GCState** %2, align 8
  %19 = getelementptr inbounds %struct.GCState, %struct.GCState* %18, i32 0, i32 6
  store i64 1024, i64* %19, align 8
  %20 = call noalias i8* @malloc(i64 1024)
  %21 = load %struct.GCState*, %struct.GCState** %2, align 8
  %22 = getelementptr inbounds %struct.GCState, %struct.GCState* %21, i32 0, i32 7
  store i8* %20, i8** %22, align 8
  %23 = load %struct.GCState*, %struct.GCState** %2, align 8
  %24 = getelementptr inbounds %struct.GCState, %struct.GCState* %23, i32 0, i32 8
  store i64 1024, i64* %24, align 8
  %25 = load %struct.GCState*, %struct.GCState** %2, align 8
  %26 = getelementptr inbounds %struct.GCState, %struct.GCState* %25, i32 0, i32 9
  store i64 0, i64* %26, align 8
  %27 = load %struct.GCState*, %struct.GCState** %2, align 8
  %28 = getelementptr inbounds %struct.GCState, %struct.GCState* %27, i32 0, i32 10
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %28, align 8
  %29 = load %struct.GCState*, %struct.GCState** %2, align 8
  %30 = getelementptr inbounds %struct.GCState, %struct.GCState* %29, i32 0, i32 11
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %30, align 8
  %31 = load %struct.GCState*, %struct.GCState** %2, align 8
  %32 = getelementptr inbounds %struct.GCState, %struct.GCState* %31, i32 0, i32 12
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %32, align 8
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
