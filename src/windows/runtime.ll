; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.GCState = type { i8*, i8*, i8, i8, i64, i64, i8, %struct.ObjectHeader*, %struct.ObjectHeader*, %struct.ObjectHeader*, [7 x %struct.AllocBlock*] }
%struct.ObjectHeader = type { %struct.AllocBlock*, %struct.ObjectHeader*, void (i8*)* }
%struct.AllocBlock = type { %struct.AllocBlock*, i32, i32, [0 x i8] }
%struct.__crt_locale_pointers = type { %struct.__crt_locale_data*, %struct.__crt_multibyte_data* }
%struct.__crt_locale_data = type opaque
%struct.__crt_multibyte_data = type opaque
%struct._SECURITY_ATTRIBUTES = type { i32, i8*, i32 }
%struct.Frame = type { i64, i64, %struct.Frame*, %struct.ObjectHeader*, [0 x %struct.ObjectHeader**] }
%struct.ThreadStartInfo = type { i64 (i8*, i8*)*, i8* }
%struct._iobuf = type { i8* }

$sprintf = comdat any

$vsprintf = comdat any

$_snprintf = comdat any

$_vsnprintf = comdat any

$printf = comdat any

$_vsprintf_l = comdat any

$_vsnprintf_l = comdat any

$__local_stdio_printf_options = comdat any

$_vfprintf_l = comdat any

$"??_C@_03OFAPEBGM@?$CFs?6?$AA@" = comdat any

$"??_C@_06IKJDLJAH@?$CFs?5?$CFp?6?$AA@" = comdat any

@gc_state = dso_local global %struct.GCState zeroinitializer, align 8
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
define dso_local void @SWERVE_gc_init() #1 {
  %1 = alloca i32, align 4
  %2 = call i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES* null, i32 0, i8* null)
  store i8* %2, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %3 = call i8* @CreateEventA(%struct._SECURITY_ATTRIBUTES* null, i32 1, i32 1, i8* null)
  store i8* %3, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 1
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), align 8
  store i64 0, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  store i8 1, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  store i32 0, i32* %1, align 4
  br label %4

4:                                                ; preds = %11, %0
  %5 = load i32, i32* %1, align 4
  %6 = icmp slt i32 %5, 7
  br i1 %6, label %7, label %14

7:                                                ; preds = %4
  %8 = load i32, i32* %1, align 4
  %9 = sext i32 %8 to i64
  %10 = getelementptr inbounds [7 x %struct.AllocBlock*], [7 x %struct.AllocBlock*]* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), i64 0, i64 %9
  store %struct.AllocBlock* null, %struct.AllocBlock** %10, align 8
  br label %11

11:                                               ; preds = %7
  %12 = load i32, i32* %1, align 4
  %13 = add nsw i32 %12, 1
  store i32 %13, i32* %1, align 4
  br label %4

14:                                               ; preds = %4
  ret void
}

declare dllimport i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES*, i32, i8*) #2

declare dllimport i8* @CreateEventA(%struct._SECURITY_ATTRIBUTES*, i32, i32, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local %struct.AllocBlock* @SWERVE_gc_add_block(i32 %0) #1 {
  %2 = alloca %struct.AllocBlock*, align 8
  %3 = alloca i32, align 4
  %4 = alloca %struct.AllocBlock*, align 8
  %5 = alloca %struct.AllocBlock*, align 8
  store i32 %0, i32* %3, align 4
  %6 = load i32, i32* %3, align 4
  %7 = icmp eq i32 %6, 0
  br i1 %7, label %8, label %9

8:                                                ; preds = %1
  call void @exit(i32 -1) #8
  unreachable

9:                                                ; preds = %1
  %10 = load i32, i32* %3, align 4
  %11 = icmp ule i32 %10, 256
  br i1 %11, label %12, label %27

12:                                               ; preds = %9
  %13 = load i32, i32* %3, align 4
  %14 = mul i32 %13, 16
  %15 = zext i32 %14 to i64
  %16 = add i64 16, %15
  %17 = call noalias i8* @malloc(i64 %16)
  %18 = bitcast i8* %17 to %struct.AllocBlock*
  store %struct.AllocBlock* %18, %struct.AllocBlock** %4, align 8
  %19 = load %struct.AllocBlock*, %struct.AllocBlock** %4, align 8
  %20 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %19, i32 0, i32 0
  store %struct.AllocBlock* null, %struct.AllocBlock** %20, align 8
  %21 = load i32, i32* %3, align 4
  %22 = load %struct.AllocBlock*, %struct.AllocBlock** %4, align 8
  %23 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %22, i32 0, i32 1
  store i32 %21, i32* %23, align 8
  %24 = load %struct.AllocBlock*, %struct.AllocBlock** %4, align 8
  %25 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %24, i32 0, i32 2
  store i32 65535, i32* %25, align 4
  %26 = load %struct.AllocBlock*, %struct.AllocBlock** %4, align 8
  store %struct.AllocBlock* %26, %struct.AllocBlock** %2, align 8
  br label %41

27:                                               ; preds = %9
  %28 = load i32, i32* %3, align 4
  %29 = zext i32 %28 to i64
  %30 = add i64 16, %29
  %31 = call noalias i8* @malloc(i64 %30)
  %32 = bitcast i8* %31 to %struct.AllocBlock*
  store %struct.AllocBlock* %32, %struct.AllocBlock** %5, align 8
  %33 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  %34 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %33, i32 0, i32 0
  store %struct.AllocBlock* null, %struct.AllocBlock** %34, align 8
  %35 = load i32, i32* %3, align 4
  %36 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  %37 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %36, i32 0, i32 1
  store i32 %35, i32* %37, align 8
  %38 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  %39 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %38, i32 0, i32 2
  store i32 1, i32* %39, align 4
  %40 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  store %struct.AllocBlock* %40, %struct.AllocBlock** %2, align 8
  br label %41

41:                                               ; preds = %27, %12
  %42 = load %struct.AllocBlock*, %struct.AllocBlock** %2, align 8
  ret %struct.AllocBlock* %42
}

; Function Attrs: noreturn
declare dso_local void @exit(i32) #3

declare dso_local noalias i8* @malloc(i64) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @SWERVE_gc_allocate(i64 %0, void (i8*)* %1) #1 {
  %3 = alloca void (i8*)*, align 8
  %4 = alloca i64, align 8
  %5 = alloca %struct.ObjectHeader*, align 8
  %6 = alloca %struct.AllocBlock*, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i64*, align 8
  store void (i8*)* %1, void (i8*)** %3, align 8
  store i64 %0, i64* %4, align 8
  %10 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %11 = call i32 @WaitForSingleObject(i8* %10, i32 -1)
  %12 = load i64, i64* %4, align 8
  %13 = icmp ule i64 %12, 256
  br i1 %13, label %14, label %83

14:                                               ; preds = %2
  %15 = load i64, i64* %4, align 8
  %16 = udiv i64 %15, 32
  %17 = load i64, i64* %4, align 8
  %18 = urem i64 %17, 32
  %19 = icmp ne i64 %18, 0
  %20 = zext i1 %19 to i64
  %21 = select i1 %19, i32 0, i32 1
  %22 = sext i32 %21 to i64
  %23 = sub i64 %16, %22
  %24 = trunc i64 %23 to i32
  store i32 %24, i32* %7, align 4
  %25 = load i32, i32* %7, align 4
  %26 = sext i32 %25 to i64
  %27 = getelementptr inbounds [7 x %struct.AllocBlock*], [7 x %struct.AllocBlock*]* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), i64 0, i64 %26
  %28 = load %struct.AllocBlock*, %struct.AllocBlock** %27, align 8
  store %struct.AllocBlock* %28, %struct.AllocBlock** %6, align 8
  br label %29

29:                                               ; preds = %39, %14
  %30 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %31 = icmp ne %struct.AllocBlock* %30, null
  br i1 %31, label %32, label %37

32:                                               ; preds = %29
  %33 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %34 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %33, i32 0, i32 2
  %35 = load i32, i32* %34, align 4
  %36 = icmp eq i32 %35, 0
  br label %37

37:                                               ; preds = %32, %29
  %38 = phi i1 [ false, %29 ], [ %36, %32 ]
  br i1 %38, label %39, label %43

39:                                               ; preds = %37
  %40 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %41 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %40, i32 0, i32 0
  %42 = load %struct.AllocBlock*, %struct.AllocBlock** %41, align 8
  store %struct.AllocBlock* %42, %struct.AllocBlock** %6, align 8
  br label %29

43:                                               ; preds = %37
  %44 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %45 = icmp eq %struct.AllocBlock* %44, null
  br i1 %45, label %46, label %61

46:                                               ; preds = %43
  %47 = load i32, i32* %7, align 4
  %48 = add nsw i32 %47, 1
  %49 = mul nsw i32 %48, 32
  %50 = call %struct.AllocBlock* @SWERVE_gc_add_block(i32 %49)
  store %struct.AllocBlock* %50, %struct.AllocBlock** %6, align 8
  %51 = load i32, i32* %7, align 4
  %52 = sext i32 %51 to i64
  %53 = getelementptr inbounds [7 x %struct.AllocBlock*], [7 x %struct.AllocBlock*]* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), i64 0, i64 %52
  %54 = load %struct.AllocBlock*, %struct.AllocBlock** %53, align 8
  %55 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %56 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %55, i32 0, i32 0
  store %struct.AllocBlock* %54, %struct.AllocBlock** %56, align 8
  %57 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %58 = load i32, i32* %7, align 4
  %59 = sext i32 %58 to i64
  %60 = getelementptr inbounds [7 x %struct.AllocBlock*], [7 x %struct.AllocBlock*]* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 10), i64 0, i64 %59
  store %struct.AllocBlock* %57, %struct.AllocBlock** %60, align 8
  br label %61

61:                                               ; preds = %46, %43
  %62 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %63 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %62, i32 0, i32 2
  %64 = load i32, i32* %63, align 4
  %65 = call i32 @llvm.cttz.i32(i32 %64, i1 true)
  store i32 %65, i32* %8, align 4
  %66 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %67 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %66, i32 0, i32 3
  %68 = load i32, i32* %8, align 4
  %69 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %70 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %69, i32 0, i32 1
  %71 = load i32, i32* %70, align 8
  %72 = mul i32 %68, %71
  %73 = zext i32 %72 to i64
  %74 = getelementptr inbounds [0 x i8], [0 x i8]* %67, i64 0, i64 %73
  %75 = bitcast i8* %74 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %75, %struct.ObjectHeader** %5, align 8
  %76 = load i32, i32* %8, align 4
  %77 = shl i32 1, %76
  %78 = xor i32 %77, -1
  %79 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %80 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %79, i32 0, i32 2
  %81 = load i32, i32* %80, align 4
  %82 = and i32 %81, %78
  store i32 %82, i32* %80, align 4
  br label %95

83:                                               ; preds = %2
  %84 = load i64, i64* %4, align 8
  %85 = trunc i64 %84 to i32
  %86 = call %struct.AllocBlock* @SWERVE_gc_add_block(i32 %85)
  store %struct.AllocBlock* %86, %struct.AllocBlock** %6, align 8
  %87 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %88 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %87, i32 0, i32 3
  %89 = getelementptr inbounds [0 x i8], [0 x i8]* %88, i64 0, i64 0
  %90 = bitcast i8* %89 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %90, %struct.ObjectHeader** %5, align 8
  %91 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %92 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %91, i32 0, i32 2
  %93 = load i32, i32* %92, align 4
  %94 = and i32 %93, -2
  store i32 %94, i32* %92, align 4
  br label %95

95:                                               ; preds = %83, %61
  %96 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %97 = bitcast %struct.ObjectHeader* %96 to i8*
  %98 = load i64, i64* %4, align 8
  call void @llvm.memset.p0i8.i64(i8* align 8 %97, i8 0, i64 %98, i1 false)
  %99 = load %struct.AllocBlock*, %struct.AllocBlock** %6, align 8
  %100 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %101 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %100, i32 0, i32 0
  store %struct.AllocBlock* %99, %struct.AllocBlock** %101, align 8
  %102 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %103 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %104 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %103, i32 0, i32 1
  store %struct.ObjectHeader* %102, %struct.ObjectHeader** %104, align 8
  %105 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  store %struct.ObjectHeader* %105, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  br label %106

106:                                              ; preds = %95
  %107 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %108 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %107, i32 0, i32 1
  %109 = bitcast %struct.ObjectHeader** %108 to i64*
  store i64* %109, i64** %9, align 8
  %110 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %111 = trunc i8 %110 to i1
  br i1 %111, label %112, label %117

112:                                              ; preds = %106
  %113 = load i64*, i64** %9, align 8
  %114 = load i64, i64* %113, align 8
  %115 = and i64 %114, -2
  %116 = load i64*, i64** %9, align 8
  store i64 %115, i64* %116, align 8
  br label %122

117:                                              ; preds = %106
  %118 = load i64*, i64** %9, align 8
  %119 = load i64, i64* %118, align 8
  %120 = or i64 %119, 1
  %121 = load i64*, i64** %9, align 8
  store i64 %120, i64* %121, align 8
  br label %122

122:                                              ; preds = %117, %112
  br label %123

123:                                              ; preds = %122
  %124 = load void (i8*)*, void (i8*)** %3, align 8
  %125 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %126 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %125, i32 0, i32 2
  store void (i8*)* %124, void (i8*)** %126, align 8
  %127 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %128 = call i32 @ReleaseMutex(i8* %127)
  %129 = load %struct.ObjectHeader*, %struct.ObjectHeader** %5, align 8
  %130 = bitcast %struct.ObjectHeader* %129 to i8*
  ret i8* %130
}

declare dllimport i32 @WaitForSingleObject(i8*, i32) #2

; Function Attrs: nounwind readnone speculatable willreturn
declare i32 @llvm.cttz.i32(i32, i1 immarg) #4

; Function Attrs: argmemonly nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #5

declare dllimport i32 @ReleaseMutex(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_mark(%struct.ObjectHeader* %0) #1 {
  %2 = alloca %struct.ObjectHeader*, align 8
  %3 = alloca i64*, align 8
  store %struct.ObjectHeader* %0, %struct.ObjectHeader** %2, align 8
  %4 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %5 = icmp eq %struct.ObjectHeader* %4, null
  br i1 %5, label %6, label %7

6:                                                ; preds = %1
  br label %42

7:                                                ; preds = %1
  %8 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %9 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %8, i32 0, i32 1
  %10 = load %struct.ObjectHeader*, %struct.ObjectHeader** %9, align 8
  %11 = ptrtoint %struct.ObjectHeader* %10 to i64
  %12 = and i64 %11, 1
  %13 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %14 = trunc i8 %13 to i1
  %15 = zext i1 %14 to i64
  %16 = select i1 %14, i32 1, i32 0
  %17 = sext i32 %16 to i64
  %18 = icmp eq i64 %12, %17
  br i1 %18, label %19, label %42

19:                                               ; preds = %7
  %20 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %21 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %22 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %21, i32 0, i32 1
  store %struct.ObjectHeader* %20, %struct.ObjectHeader** %22, align 8
  %23 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  store %struct.ObjectHeader* %23, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  br label %24

24:                                               ; preds = %19
  %25 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %26 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %25, i32 0, i32 1
  %27 = bitcast %struct.ObjectHeader** %26 to i64*
  store i64* %27, i64** %3, align 8
  %28 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %29 = trunc i8 %28 to i1
  br i1 %29, label %30, label %35

30:                                               ; preds = %24
  %31 = load i64*, i64** %3, align 8
  %32 = load i64, i64* %31, align 8
  %33 = and i64 %32, -2
  %34 = load i64*, i64** %3, align 8
  store i64 %33, i64* %34, align 8
  br label %40

35:                                               ; preds = %24
  %36 = load i64*, i64** %3, align 8
  %37 = load i64, i64* %36, align 8
  %38 = or i64 %37, 1
  %39 = load i64*, i64** %3, align 8
  store i64 %38, i64* %39, align 8
  br label %40

40:                                               ; preds = %35, %30
  br label %41

41:                                               ; preds = %40
  br label %42

42:                                               ; preds = %6, %41, %7
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_trace_helper(i8* %0, i8* %1, %struct.ObjectHeader* %2) #1 {
  %4 = alloca %struct.ObjectHeader*, align 8
  %5 = alloca i8*, align 8
  %6 = alloca i8*, align 8
  store %struct.ObjectHeader* %2, %struct.ObjectHeader** %4, align 8
  store i8* %1, i8** %5, align 8
  store i8* %0, i8** %6, align 8
  %7 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  call void @SWERVE_gc_mark(%struct.ObjectHeader* %7)
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_check(%struct.Frame* %0, %struct.ObjectHeader* %1) #1 {
  %3 = alloca %struct.ObjectHeader*, align 8
  %4 = alloca %struct.Frame*, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.ObjectHeader**, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  store %struct.ObjectHeader* %1, %struct.ObjectHeader** %3, align 8
  store %struct.Frame* %0, %struct.Frame** %4, align 8
  %11 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 1
  %12 = trunc i8 %11 to i1
  br i1 %12, label %13, label %14

13:                                               ; preds = %2
  br label %66

14:                                               ; preds = %2
  %15 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  %16 = trunc i8 %15 to i1
  br i1 %16, label %17, label %66

17:                                               ; preds = %14
  %18 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %19 = call i32 @WaitForSingleObject(i8* %18, i32 -1)
  %20 = load %struct.ObjectHeader*, %struct.ObjectHeader** %3, align 8
  call void @SWERVE_gc_mark(%struct.ObjectHeader* %20)
  br label %21

21:                                               ; preds = %49, %17
  %22 = load %struct.Frame*, %struct.Frame** %4, align 8
  %23 = icmp ne %struct.Frame* %22, null
  br i1 %23, label %24, label %53

24:                                               ; preds = %21
  %25 = load %struct.Frame*, %struct.Frame** %4, align 8
  %26 = getelementptr inbounds %struct.Frame, %struct.Frame* %25, i32 0, i32 3
  %27 = load %struct.ObjectHeader*, %struct.ObjectHeader** %26, align 8
  call void @SWERVE_gc_mark(%struct.ObjectHeader* %27)
  store i64 0, i64* %5, align 8
  br label %28

28:                                               ; preds = %46, %24
  %29 = load i64, i64* %5, align 8
  %30 = load %struct.Frame*, %struct.Frame** %4, align 8
  %31 = getelementptr inbounds %struct.Frame, %struct.Frame* %30, i32 0, i32 0
  %32 = load i64, i64* %31, align 8
  %33 = icmp ult i64 %29, %32
  br i1 %33, label %34, label %49

34:                                               ; preds = %28
  %35 = load %struct.Frame*, %struct.Frame** %4, align 8
  %36 = getelementptr inbounds %struct.Frame, %struct.Frame* %35, i32 0, i32 4
  %37 = load i64, i64* %5, align 8
  %38 = getelementptr inbounds [0 x %struct.ObjectHeader**], [0 x %struct.ObjectHeader**]* %36, i64 0, i64 %37
  %39 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %38, align 8
  store %struct.ObjectHeader** %39, %struct.ObjectHeader*** %6, align 8
  %40 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %6, align 8
  %41 = icmp ne %struct.ObjectHeader** %40, null
  br i1 %41, label %42, label %45

42:                                               ; preds = %34
  %43 = load %struct.ObjectHeader**, %struct.ObjectHeader*** %6, align 8
  %44 = load %struct.ObjectHeader*, %struct.ObjectHeader** %43, align 8
  call void @SWERVE_gc_mark(%struct.ObjectHeader* %44)
  br label %45

45:                                               ; preds = %42, %34
  br label %46

46:                                               ; preds = %45
  %47 = load i64, i64* %5, align 8
  %48 = add i64 %47, 1
  store i64 %48, i64* %5, align 8
  br label %28

49:                                               ; preds = %28
  %50 = load %struct.Frame*, %struct.Frame** %4, align 8
  %51 = getelementptr inbounds %struct.Frame, %struct.Frame* %50, i32 0, i32 2
  %52 = load %struct.Frame*, %struct.Frame** %51, align 8
  store %struct.Frame* %52, %struct.Frame** %4, align 8
  br label %21

53:                                               ; preds = %21
  %54 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 0), align 8
  %55 = call i32 @ReleaseMutex(i8* %54)
  store i64 1, i64* %7, align 8
  %56 = load i64, i64* %7, align 8
  %57 = atomicrmw add i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), i64 %56 seq_cst
  %58 = add i64 %57, %56
  store i64 %58, i64* %8, align 8
  %59 = load i64, i64* %8, align 8
  %60 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  %61 = call i32 @WaitForSingleObject(i8* %60, i32 -1)
  store i64 1, i64* %9, align 8
  %62 = load i64, i64* %9, align 8
  %63 = atomicrmw sub i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), i64 %62 seq_cst
  %64 = sub i64 %63, %62
  store i64 %64, i64* %10, align 8
  %65 = load i64, i64* %10, align 8
  br label %66

66:                                               ; preds = %13, %53, %14
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
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 8 %9, i8* align 8 %10, i64 16, i1 false)
  %11 = load i8*, i8** %2, align 8
  call void @free(i8* %11)
  %12 = bitcast %struct.Frame* %4 to i8*
  call void @llvm.memset.p0i8.i64(i8* align 8 %12, i8 0, i64 32, i1 false)
  %13 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 0
  %14 = load i64 (i8*, i8*)*, i64 (i8*, i8*)** %13, align 8
  %15 = getelementptr inbounds %struct.ThreadStartInfo, %struct.ThreadStartInfo* %3, i32 0, i32 1
  %16 = load i8*, i8** %15, align 8
  %17 = bitcast %struct.Frame* %4 to i8*
  %18 = call i64 %14(i8* %17, i8* %16)
  store i64 1, i64* %5, align 8
  %19 = load i64, i64* %5, align 8
  %20 = atomicrmw sub i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), i64 %19 seq_cst
  %21 = sub i64 %20, %19
  store i64 %21, i64* %6, align 8
  %22 = load i64, i64* %6, align 8
  ret void
}

; Function Attrs: argmemonly nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #6

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
  %17 = atomicrmw add i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), i64 %16 seq_cst
  %18 = add i64 %17, %16
  store i64 %18, i64* %7, align 8
  %19 = load i64, i64* %7, align 8
  %20 = load %struct.ThreadStartInfo*, %struct.ThreadStartInfo** %5, align 8
  %21 = bitcast %struct.ThreadStartInfo* %20 to i8*
  %22 = call i64 @_beginthread(void (i8*)* @SWERVE_begin_thread_helper, i32 0, i8* %21)
  ret void
}

declare dso_local i64 @_beginthread(void (i8*)*, i32, i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_main() #1 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.ObjectHeader*, align 8
  %3 = alloca i64*, align 8
  %4 = alloca %struct.ObjectHeader*, align 8
  %5 = alloca %struct.AllocBlock*, align 8
  %6 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  br label %7

7:                                                ; preds = %0, %111
  %8 = call i32 @SwitchToThread()
  %9 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), align 8
  %10 = icmp eq i64 %9, 0
  br i1 %10, label %11, label %12

11:                                               ; preds = %7
  ret void

12:                                               ; preds = %7
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %13 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  %14 = call i32 @ResetEvent(i8* %13)
  store i8 1, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  br label %15

15:                                               ; preds = %12, %21
  %16 = call i32 @SwitchToThread()
  %17 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 4), align 8
  %18 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  %19 = icmp eq i64 %17, %18
  br i1 %19, label %20, label %21

20:                                               ; preds = %15
  br label %22

21:                                               ; preds = %15
  br label %15

22:                                               ; preds = %20
  store i8 1, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 1
  br label %23

23:                                               ; preds = %60, %22
  %24 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %25 = icmp ne %struct.ObjectHeader* %24, null
  br i1 %25, label %26, label %61

26:                                               ; preds = %23
  %27 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  store %struct.ObjectHeader* %27, %struct.ObjectHeader** %2, align 8
  %28 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %29 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %28, i32 0, i32 1
  %30 = load %struct.ObjectHeader*, %struct.ObjectHeader** %29, align 8
  %31 = ptrtoint %struct.ObjectHeader* %30 to i64
  %32 = and i64 %31, -2
  %33 = inttoptr i64 %32 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %33, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 8), align 8
  %34 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %35 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %34, i32 0, i32 2
  %36 = load void (i8*)*, void (i8*)** %35, align 8
  %37 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %38 = bitcast %struct.ObjectHeader* %37 to i8*
  call void %36(i8* %38)
  %39 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  %40 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %41 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %40, i32 0, i32 1
  store %struct.ObjectHeader* %39, %struct.ObjectHeader** %41, align 8
  %42 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  store %struct.ObjectHeader* %42, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  br label %43

43:                                               ; preds = %26
  %44 = load %struct.ObjectHeader*, %struct.ObjectHeader** %2, align 8
  %45 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %44, i32 0, i32 1
  %46 = bitcast %struct.ObjectHeader** %45 to i64*
  store i64* %46, i64** %3, align 8
  %47 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %48 = trunc i8 %47 to i1
  br i1 %48, label %49, label %54

49:                                               ; preds = %43
  %50 = load i64*, i64** %3, align 8
  %51 = load i64, i64* %50, align 8
  %52 = and i64 %51, -2
  %53 = load i64*, i64** %3, align 8
  store i64 %52, i64* %53, align 8
  br label %59

54:                                               ; preds = %43
  %55 = load i64*, i64** %3, align 8
  %56 = load i64, i64* %55, align 8
  %57 = or i64 %56, 1
  %58 = load i64*, i64** %3, align 8
  store i64 %57, i64* %58, align 8
  br label %59

59:                                               ; preds = %54, %49
  br label %60

60:                                               ; preds = %59
  br label %23

61:                                               ; preds = %23
  %62 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  store %struct.ObjectHeader* %62, %struct.ObjectHeader** %4, align 8
  br label %63

63:                                               ; preds = %66, %61
  %64 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %65 = icmp ne %struct.ObjectHeader* %64, null
  br i1 %65, label %66, label %97

66:                                               ; preds = %63
  %67 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %68 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %67, i32 0, i32 0
  %69 = load %struct.AllocBlock*, %struct.AllocBlock** %68, align 8
  store %struct.AllocBlock* %69, %struct.AllocBlock** %5, align 8
  %70 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %71 = ptrtoint %struct.ObjectHeader* %70 to i64
  %72 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  %73 = ptrtoint %struct.AllocBlock* %72 to i64
  %74 = sub nsw i64 %71, %73
  %75 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  %76 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %75, i32 0, i32 1
  %77 = load i32, i32* %76, align 8
  %78 = zext i32 %77 to i64
  %79 = sdiv i64 %74, %78
  %80 = trunc i64 %79 to i32
  store i32 %80, i32* %6, align 4
  %81 = load i32, i32* %6, align 4
  %82 = zext i32 %81 to i64
  %83 = shl i64 1, %82
  %84 = xor i64 %83, -1
  %85 = load %struct.AllocBlock*, %struct.AllocBlock** %5, align 8
  %86 = getelementptr inbounds %struct.AllocBlock, %struct.AllocBlock* %85, i32 0, i32 2
  %87 = load i32, i32* %86, align 4
  %88 = zext i32 %87 to i64
  %89 = and i64 %88, %84
  %90 = trunc i64 %89 to i32
  store i32 %90, i32* %86, align 4
  %91 = load %struct.ObjectHeader*, %struct.ObjectHeader** %4, align 8
  %92 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %91, i32 0, i32 1
  %93 = load %struct.ObjectHeader*, %struct.ObjectHeader** %92, align 8
  %94 = ptrtoint %struct.ObjectHeader* %93 to i64
  %95 = and i64 %94, -2
  %96 = inttoptr i64 %95 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %96, %struct.ObjectHeader** %4, align 8
  br label %63

97:                                               ; preds = %63
  %98 = load %struct.ObjectHeader*, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  store %struct.ObjectHeader* %98, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 7), align 8
  store %struct.ObjectHeader* null, %struct.ObjectHeader** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 9), align 8
  %99 = load i8, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  %100 = trunc i8 %99 to i1
  %101 = xor i1 %100, true
  %102 = zext i1 %101 to i8
  store i8 %102, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 6), align 8
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 3), align 1
  store i8 0, i8* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 2), align 8
  %103 = load i8*, i8** getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 1), align 8
  %104 = call i32 @SetEvent(i8* %103)
  br label %105

105:                                              ; preds = %97, %110
  %106 = call i32 @SwitchToThread()
  %107 = load i64, i64* getelementptr inbounds (%struct.GCState, %struct.GCState* @gc_state, i32 0, i32 5), align 8
  %108 = icmp eq i64 %107, 0
  br i1 %108, label %109, label %110

109:                                              ; preds = %105
  br label %111

110:                                              ; preds = %105
  br label %105

111:                                              ; preds = %109
  br label %7
}

declare dllimport i32 @SwitchToThread() #2

declare dllimport i32 @ResetEvent(i8*) #2

declare dllimport i32 @SetEvent(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_display(i8* %0) #1 {
  %2 = alloca i8*, align 8
  store i8* %0, i8** %2, align 8
  %3 = load i8*, i8** %2, align 8
  %4 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @"??_C@_03OFAPEBGM@?$CFs?6?$AA@", i64 0, i64 0), i8* %3)
  ret void
}

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
declare void @llvm.va_start(i8*) #7

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
declare void @llvm.va_end(i8*) #7

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
attributes #3 = { noreturn "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="none" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #4 = { nounwind readnone speculatable willreturn }
attributes #5 = { argmemonly nounwind willreturn writeonly }
attributes #6 = { argmemonly nounwind willreturn }
attributes #7 = { nounwind }
attributes #8 = { noreturn }

!llvm.linker.options = !{!0, !0}
!llvm.module.flags = !{!1, !2}
!llvm.ident = !{!3}

!0 = !{!"/DEFAULTLIB:uuid.lib"}
!1 = !{i32 1, !"wchar_size", i32 2}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{!"clang version 11.1.0"}
