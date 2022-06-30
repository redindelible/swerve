; ModuleID = 'runtime.c'
source_filename = "runtime.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.29.30133"

%struct.GCState = type { i8*, i8*, i8* }
%struct.ObjectHeader = type { %struct.ObjectHeader*, i8, i8* }

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i8* @SWERVE_gc_allocate(%struct.GCState* noundef %0, i64 noundef %1, i8* noundef %2) #0 {
  %4 = alloca i8*, align 8
  %5 = alloca i64, align 8
  %6 = alloca %struct.GCState*, align 8
  %7 = alloca %struct.ObjectHeader*, align 8
  store i8* %2, i8** %4, align 8
  store i64 %1, i64* %5, align 8
  store %struct.GCState* %0, %struct.GCState** %6, align 8
  %8 = load i64, i64* %5, align 8
  %9 = call noalias i8* @malloc(i64 noundef %8)
  %10 = bitcast i8* %9 to %struct.ObjectHeader*
  store %struct.ObjectHeader* %10, %struct.ObjectHeader** %7, align 8
  %11 = load %struct.GCState*, %struct.GCState** %6, align 8
  %12 = getelementptr inbounds %struct.GCState, %struct.GCState* %11, i32 0, i32 1
  %13 = load i8*, i8** %12, align 8
  %14 = bitcast i8* %13 to %struct.ObjectHeader*
  %15 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %16 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %15, i32 0, i32 0
  store %struct.ObjectHeader* %14, %struct.ObjectHeader** %16, align 8
  %17 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %18 = bitcast %struct.ObjectHeader* %17 to i8*
  %19 = load %struct.GCState*, %struct.GCState** %6, align 8
  %20 = getelementptr inbounds %struct.GCState, %struct.GCState* %19, i32 0, i32 1
  store i8* %18, i8** %20, align 8
  %21 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %22 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %21, i32 0, i32 1
  store i8 1, i8* %22, align 8
  %23 = load i8*, i8** %4, align 8
  %24 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %25 = getelementptr inbounds %struct.ObjectHeader, %struct.ObjectHeader* %24, i32 0, i32 2
  store i8* %23, i8** %25, align 8
  %26 = load %struct.ObjectHeader*, %struct.ObjectHeader** %7, align 8
  %27 = bitcast %struct.ObjectHeader* %26 to i8*
  ret i8* %27
}

declare dso_local noalias i8* @malloc(i64 noundef) #1

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 2}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 1}
!3 = !{!"clang version 14.0.4"}
