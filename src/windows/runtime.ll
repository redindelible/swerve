; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.__crt_locale_pointers = type { %struct.__crt_locale_data*, %struct.__crt_multibyte_data* }
%struct.__crt_locale_data = type opaque
%struct.__crt_multibyte_data = type opaque
%struct.GCState = type { i8*, i8, %struct.ObjectHeader*, %struct.ObjectHeader*, %struct.ObjectHeader* }
%struct.ObjectHeader = type { %struct.ObjectHeader*, i8, i8* }
%struct.Frame = type { i64, %struct.Frame*, i8*, [0 x i8**] }
%struct._SECURITY_ATTRIBUTES = type { i32, i8*, i32 }

$sprintf = comdat any

$vsprintf = comdat any

$_snprintf = comdat any

$_vsnprintf = comdat any

$_vsprintf_l = comdat any

$_vsnprintf_l = comdat any

$__local_stdio_printf_options = comdat any

@__local_stdio_printf_options._OptionsStorage = internal global i64 0, align 8

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @sprintf(i8* noundef %0, i8* noundef %1, ...) #0 comdat {
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
  %11 = call i32 @_vsprintf_l(i8* noundef %10, i8* noundef %9, %struct.__crt_locale_pointers* noundef null, i8* noundef %8)
  store i32 %11, i32* %5, align 4
  %12 = bitcast i8** %6 to i8*
  call void @llvm.va_end(i8* %12)
  %13 = load i32, i32* %5, align 4
  ret i32 %13
}

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @vsprintf(i8* noundef %0, i8* noundef %1, i8* noundef %2) #0 comdat {
  %4 = alloca i8*, align 8
  %5 = alloca i8*, align 8
  %6 = alloca i8*, align 8
  store i8* %2, i8** %4, align 8
  store i8* %1, i8** %5, align 8
  store i8* %0, i8** %6, align 8
  %7 = load i8*, i8** %4, align 8
  %8 = load i8*, i8** %5, align 8
  %9 = load i8*, i8** %6, align 8
  %10 = call i32 @_vsnprintf_l(i8* noundef %9, i64 noundef -1, i8* noundef %8, %struct.__crt_locale_pointers* noundef null, i8* noundef %7)
  ret i32 %10
}

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_snprintf(i8* noundef %0, i64 noundef %1, i8* noundef %2, ...) #0 comdat {
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
  %14 = call i32 @_vsnprintf(i8* noundef %13, i64 noundef %12, i8* noundef %11, i8* noundef %10)
  store i32 %14, i32* %7, align 4
  %15 = bitcast i8** %8 to i8*
  call void @llvm.va_end(i8* %15)
  %16 = load i32, i32* %7, align 4
  ret i32 %16
}

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vsnprintf(i8* noundef %0, i64 noundef %1, i8* noundef %2, i8* noundef %3) #0 comdat {
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
  %13 = call i32 @_vsnprintf_l(i8* noundef %12, i64 noundef %11, i8* noundef %10, %struct.__crt_locale_pointers* noundef null, i8* noundef %9)
  ret i32 %13
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @SWERVE_gc_allocate(%struct.GCState* noundef %0, i64 noundef %1, i8* noundef %2) #0 {
  %4 = alloca i8*, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.GCState*, align 8
  %7 = alloca %struct.ObjectHeader*, align 8
  store i8* %2, i8** %4, align 8
  store i64 %1, i64* %5, align 8
  store %struct.GCState* %0, %struct.GCState** %6, align 8
  %8 = load %struct.GCState*, %struct.GCState** %6, align 8
  %9 = getelementptr inbounds %struct.GCState, %struct.GCState* %8, i32 0, i32 0
  %10 = load i8*, i8** %9, align 8
  %11 = call i32 @WaitForSingleObject(i8* noundef %10, i32 noundef -1)
  %12 = load i64, i64* %5, align 8
  %13 = call noalias i8* @malloc(i64 noundef %12)
  %14 = bitcast i8* %13 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %14, %struct.ObjectHeader** %7, align 8
  %15 = load %struct.GCState*, %struct.GCState** %6, align 8
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 3
  %17 = load %struct.ObjectHeader*, %struct.ObjectHeader** %16, align 8
  %18 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %19 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %18, i32 0, i32 0
  store %struct.ObjectHeader* %17, %struct.ObjectHeader** %19, align 8
  %20 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %21 = load %struct.GCState*, %struct.GCState** %6, align 8
  %22 = getelementptr inbounds %struct.GCState, %struct.GCState* %21, i32 0, i32 3
  store %struct.ObjectHeader* %20, %struct.ObjectHeader** %22, align 8
  %23 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %24 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %23, i32 0, i32 1
  store i8 1, i8* %24, align 8
  %25 = load i8*, i8** %4, align 8
  %26 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %27 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %26, i32 0, i32 2
  store i8* %25, i8** %27, align 8
  %28 = load %struct.GCState*, %struct.GCState** %6, align 8
  %29 = getelementptr inbounds %struct.GCState, %struct.GCState* %28, i32 0, i32 0
  %30 = load i8*, i8** %29, align 8
  %31 = call i32 @ReleaseMutex(i8* noundef %30)
  %32 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %33 = bitcast %struct.ObjectHeader* %32 to i8*
  ret i8* %33
}

declare dllimport i32 @WaitForSingleObject(i8* noundef, i32 noundef) #1

declare dso_local noalias i8* @malloc(i64 noundef) #1

declare dllimport i32 @ReleaseMutex(i8* noundef) #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_check(%struct.Frame* noundef %0, %struct.GCState* noundef %1) #0 {
  %3 = alloca %struct.GCState*, align 8
  %4 = alloca %struct.Frame*, align 8
  store %struct.GCState* %1, %struct.GCState** %3, align 8
  store %struct.Frame* %0, %struct.Frame** %4, align 8
  %5 = load %struct.GCState*, %struct.GCState** %3, align 8
  %6 = getelementptr inbounds %struct.GCState, %struct.GCState* %5, i32 0, i32 1
  %7 = load i8, i8* %6, align 8
  %8 = trunc i8 %7 to i1
  br i1 %8, label %9, label %18

9:                                                ; preds = %2
  %10 = load %struct.GCState*, %struct.GCState** %3, align 8
  %11 = getelementptr inbounds %struct.GCState, %struct.GCState* %10, i32 0, i32 0
  %12 = load i8*, i8** %11, align 8
  %13 = call i32 @WaitForSingleObject(i8* noundef %12, i32 noundef -1)
  %14 = load %struct.GCState*, %struct.GCState** %3, align 8
  %15 = getelementptr inbounds %struct.GCState, %struct.GCState* %14, i32 0, i32 0
  %16 = load i8*, i8** %15, align 8
  %17 = call i32 @ReleaseMutex(i8* noundef %16)
  br label %18

18:                                               ; preds = %9, %2
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @SWERVE_gc_init(%struct.GCState* noundef %0) #0 {
  %2 = alloca %struct.GCState*, align 8
  store %struct.GCState* %0, %struct.GCState** %2, align 8
  %3 = call i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES* noundef null, i32 noundef 0, i8* noundef null)
  %4 = load %struct.GCState*, %struct.GCState** %2, align 8
  %5 = getelementptr inbounds %struct.GCState, %struct.GCState* %4, i32 0, i32 0
  store i8* %3, i8** %5, align 8
  %6 = load %struct.GCState*, %struct.GCState** %2, align 8
  %7 = getelementptr inbounds %struct.GCState, %struct.GCState* %6, i32 0, i32 1
  store i8 0, i8* %7, align 8
  %8 = load %struct.GCState*, %struct.GCState** %2, align 8
  %9 = getelementptr inbounds %struct.GCState, %struct.GCState* %8, i32 0, i32 2
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %9, align 8
  %10 = load %struct.GCState*, %struct.GCState** %2, align 8
  %11 = getelementptr inbounds %struct.GCState, %struct.GCState* %10, i32 0, i32 3
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %11, align 8
  %12 = load %struct.GCState*, %struct.GCState** %2, align 8
  %13 = getelementptr inbounds %struct.GCState, %struct.GCState* %12, i32 0, i32 4
  store %struct.ObjectHeader* null, %struct.ObjectHeader** %13, align 8
  ret void
}

declare dllimport i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES* noundef, i32 noundef, i8* noundef) #1

; Function Attrs: nofree nosync nounwind willreturn
declare void @llvm.va_start(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vsprintf_l(i8* noundef %0, i8* noundef %1, %struct.__crt_locale_pointers* noundef %2, i8* noundef %3) #0 comdat {
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
  %13 = call i32 @_vsnprintf_l(i8* noundef %12, i64 noundef -1, i8* noundef %11, %struct.__crt_locale_pointers* noundef %10, i8* noundef %9)
  ret i32 %13
}

; Function Attrs: nofree nosync nounwind willreturn
declare void @llvm.va_end(i8*) #2

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i32 @_vsnprintf_l(i8* noundef %0, i64 noundef %1, i8* noundef %2, %struct.__crt_locale_pointers* noundef %3, i8* noundef %4) #0 comdat {
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
  %20 = call i32 @__stdio_common_vsprintf(i64 noundef %19, i8* noundef %16, i64 noundef %15, i8* noundef %14, %struct.__crt_locale_pointers* noundef %13, i8* noundef %12)
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

declare dso_local i32 @__stdio_common_vsprintf(i64 noundef, i8* noundef, i64 noundef, i8* noundef, %struct.__crt_locale_pointers* noundef, i8* noundef) #1

; Function Attrs: noinline nounwind optnone uwtable
define linkonce_odr dso_local i64* @__local_stdio_printf_options() #0 comdat {
  ret i64* @__local_stdio_printf_options._OptionsStorage
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nofree nosync nounwind willreturn }

!llvm.linker.options = !{!0, !0}
!llvm.module.flags = !{!1, !2, !3}
!llvm.ident = !{!4}

!0 = !{!"/DEFAULTLIB:uuid.lib"}
!1 = !{i32 1, !"wchar_size", i32 2}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{!"clang version 14.0.4"}
