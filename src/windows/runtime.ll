; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.GCState = type { i8*, i8*, i8*, i8* }
%struct.ObjectHeader = type { %struct.ObjectHeader*, i8, i8* }
%struct._SECURITY_ATTRIBUTES = type { i32, i8*, i32 }

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
  %16 = getelementptr inbounds %struct.GCState, %struct.GCState* %15, i32 0, i32 2
  %17 = load i8*, i8** %16, align 8
  %18 = bitcast i8* %17 to %struct.ObjectHeader*
  %19 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %20 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %19, i32 0, i32 0
  store %struct.ObjectHeader* %18, %struct.ObjectHeader** %20, align 8
  %21 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %22 = bitcast %struct.ObjectHeader* %21 to i8*
  %23 = load %struct.GCState*, %struct.GCState** %6, align 8
  %24 = getelementptr inbounds %struct.GCState, %struct.GCState* %23, i32 0, i32 2
  store i8* %22, i8** %24, align 8
  %25 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %26 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %25, i32 0, i32 1
  store i8 1, i8* %26, align 8
  %27 = load i8*, i8** %4, align 8
  %28 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %29 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %28, i32 0, i32 2
  store i8* %27, i8** %29, align 8
  %30 = load %struct.GCState*, %struct.GCState** %6, align 8
  %31 = getelementptr inbounds %struct.GCState, %struct.GCState* %30, i32 0, i32 0
  %32 = load i8*, i8** %31, align 8
  %33 = call i32 @ReleaseMutex(i8* noundef %32)
  %34 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %35 = bitcast %struct.ObjectHeader* %34 to i8*
  ret i8* %35
}

declare dllimport i32 @WaitForSingleObject(i8* noundef, i32 noundef) #1

declare dso_local noalias i8* @malloc(i64 noundef) #1

declare dllimport i32 @ReleaseMutex(i8* noundef) #1

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
  store i8* null, i8** %7, align 8
  %8 = load %struct.GCState*, %struct.GCState** %2, align 8
  %9 = getelementptr inbounds %struct.GCState, %struct.GCState* %8, i32 0, i32 2
  store i8* null, i8** %9, align 8
  %10 = load %struct.GCState*, %struct.GCState** %2, align 8
  %11 = getelementptr inbounds %struct.GCState, %struct.GCState* %10, i32 0, i32 3
  store i8* null, i8** %11, align 8
  ret void
}

declare dllimport i8* @CreateMutexA(%struct._SECURITY_ATTRIBUTES* noundef, i32 noundef, i8* noundef) #1

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.linker.options = !{!0, !0}
!llvm.module.flags = !{!1, !2, !3}
!llvm.ident = !{!4}

!0 = !{!"/DEFAULTLIB:uuid.lib"}
!1 = !{i32 1, !"wchar_size", i32 2}
!2 = !{i32 7, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{!"clang version 14.0.4"}
