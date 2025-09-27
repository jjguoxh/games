import SwiftUI
import ActivityKit

struct ContentView: View {
    // Drag & timer states
    @State private var dragOffset: CGFloat = 0
    @State private var startDragOffset: CGFloat = 0
    @State private var isDragging: Bool = false
    @State private var liveActivity: Any? = nil
    @State private var targetDate: Date? = nil
    @State private var countdownRemaining: TimeInterval? = nil

    // Base time is now
    @State private var baseDate: Date = Date()

    // Layout constants
    private let baselineRightPadding: CGFloat = 24
    private let topMargin: CGFloat = 80
    private let hangerLength: CGFloat = 32
    private let ringOuterRadius: CGFloat = 18
    private let ringInnerRadius: CGFloat = 12
    private let ringHitSize: CGFloat = 60
    private let pointsPerMinute: CGFloat = 6  // 每分钟对应像素
    private let tickEveryMinutes: Int = 10
    private let snapEveryMinutes: Int = 1
    private let tickLineLength: CGFloat = 160

    var body: some View {
        GeometryReader { geo in
            let baselineOffsetX: CGFloat = 30
            let baselineX = geo.size.width - baselineRightPadding - baselineOffsetX
            let hangerOffsetX: CGFloat = 30
            let ringX = baselineX - hangerOffsetX
            let minY = topMargin + hangerLength
            let maxY = geo.size.height - 40
            let ringY = max(minY, min(minY + dragOffset, maxY))
            let availableHeight = maxY - minY
            let totalMinutes = Int(availableHeight / pointsPerMinute)
            // 原始拖拽对应分钟
            let selectedMinutesRaw = max(0, Int((ringY - minY) / pointsPerMinute))
            // 对齐到 1 分钟刻度（四舍五入到最近步长），并限制范围
            let selectedMinutesSnapped = min(
                totalMinutes,
                max(0, Int(round(Double(selectedMinutesRaw) / Double(snapEveryMinutes))) * snapEveryMinutes)
            )
            let selectedTimeSnapped = Calendar.current.date(byAdding: .minute, value: selectedMinutesSnapped, to: baseDate) ?? baseDate

            ZStack(alignment: .topLeading) {
                // Background
                Color(UIColor.systemBackground).ignoresSafeArea()

                // Current time header
                VStack(alignment: .leading, spacing: 8) {
                    Text("当前时间: \(formatTime(baseDate))")
                        .font(.headline)
                    if let countdownRemaining {
                        Text("倒计时: \(formatRemaining(countdownRemaining))")
                            .font(.subheadline)
                            .foregroundColor(.accentColor)
                    } else {
                        Text("拖拽右上圆环设置定时器时间")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.top, 20)
                .padding(.horizontal, 16)

                // Timeline scale with ticks every 10 minutes
                timelineScale(minY: minY,
                              maxY: maxY,
                              baselineX: baselineX,
                              minutesPerPoint: pointsPerMinute,
                              tickEveryMinutes: tickEveryMinutes,
                              tickLineLength: tickLineLength,
                              baseDate: baseDate)

                // Selected time label to the left of baseline, aligned with ringY
                Text(formatTime(selectedTimeSnapped))
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(.primary)
                    .position(x: baselineX - tickLineLength - 20, y: ringY)

                // Hanger vertical line segment (extends to the ring top, shifted left)
                Path { path in
                    path.move(to: CGPoint(x: ringX, y: topMargin))
                    path.addLine(to: CGPoint(x: ringX, y: ringY - ringOuterRadius))
                }
                .stroke(Color.secondary, style: StrokeStyle(lineWidth: 2, lineCap: .round))

                // Concentric ring hanging from the line
                ZStack {
                    Circle()
                        .stroke(Color.accentColor.opacity(isDragging ? 0.9 : 0.7), lineWidth: 5)
                        .frame(width: ringOuterRadius * 2, height: ringOuterRadius * 2)
                    Circle()
                        .stroke(Color.accentColor.opacity(isDragging ? 0.6 : 0.4), lineWidth: 3)
                        .frame(width: ringInnerRadius * 2, height: ringInnerRadius * 2)
                }
                .frame(width: ringHitSize, height: ringHitSize)
                .contentShape(Rectangle())
                .scaleEffect(isDragging ? 1.15 : 1.0)
                .shadow(color: Color.accentColor.opacity(isDragging ? 0.35 : 0.0), radius: isDragging ? 6 : 0, x: 0, y: 2)
                .animation(.spring(response: 0.25, dampingFraction: 0.8), value: isDragging)
                .zIndex(10)
                .position(x: ringX, y: ringY)
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            if !isDragging {
                                isDragging = true
                                startDragOffset = dragOffset
                            }
                            dragOffset = startDragOffset + value.translation.height
                        }
                        .onEnded { _ in
                            isDragging = false
                            // 设定目标时间并开启倒计时
                            let minutes = selectedMinutesSnapped
                            let target = Calendar.current.date(byAdding: .minute, value: minutes, to: baseDate) ?? Date()
                            targetDate = target
                            countdownRemaining = target.timeIntervalSince(Date())

                            // 安排本地通知提醒（在后台也能提醒）
                            if let remaining = countdownRemaining, remaining > 0 {
                                NotificationManager.scheduleCountdown(after: remaining)
                                // 启动 Live Activity 展示到锁屏 / 动态岛
                                if #available(iOS 16.1, *) {
                                    let attributes = CountdownActivityAttributes(name: "计时")
                                    let state = CountdownActivityAttributes.ContentState(remainingSeconds: Int(remaining), endDate: target)
                                    do {
                                        let activity = try Activity<CountdownActivityAttributes>.request(attributes: attributes, contentState: state)
                                        liveActivity = activity
                                    } catch {
                                        liveActivity = nil
                                    }
                                }
                            }
                        }
                )

                // 拖拽时在圆环左侧显示预览倒计时
                if isDragging {
                    let previewRemaining = max(0, selectedTimeSnapped.timeIntervalSince(Date()))
                    Text(formatRemaining(previewRemaining))
                        .font(.caption)
                        .foregroundColor(.accentColor)
                        .allowsHitTesting(false)
                        .position(x: ringX - ringOuterRadius - 28, y: ringY)
                }
            }
            .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
                // 滚动时间基准保持跟随当前时间
                baseDate = Date()

                guard let targetDate else { return }
                let remaining = targetDate.timeIntervalSince(Date())
                if remaining <= 0 {
                    countdownRemaining = nil
                    self.targetDate = nil
                    // 结束 Live Activity
                    if #available(iOS 16.1, *), let activity = liveActivity as? Activity<CountdownActivityAttributes> {
                        Task { await activity.end(dismissalPolicy: .immediate) }
                        liveActivity = nil
                    }
                } else {
                    countdownRemaining = remaining
                    // 更新 Live Activity 剩余时间
                    if #available(iOS 16.1, *), let activity = liveActivity as? Activity<CountdownActivityAttributes> {
                        let state = CountdownActivityAttributes.ContentState(remainingSeconds: Int(remaining), endDate: targetDate)
                        Task { await activity.update(using: state) }
                    }
                }
            }
        }
    }

    // 绘制刻度
    @ViewBuilder
    private func timelineScale(
        minY: CGFloat,
        maxY: CGFloat,
        baselineX: CGFloat,
        minutesPerPoint: CGFloat,
        tickEveryMinutes: Int,
        tickLineLength: CGFloat,
        baseDate: Date
    ) -> some View {
        let totalMinutes = Int((maxY - minY) / minutesPerPoint)
        let step = max(1, tickEveryMinutes)
        let ticks = stride(from: 0, through: totalMinutes, by: step).map { $0 }

        ForEach(Array(ticks.enumerated()), id: \.offset) { idx, minute in
            let y = minY + CGFloat(minute) * minutesPerPoint
            let isHour = minute % 60 == 0
            Path { path in
                path.move(to: CGPoint(x: baselineX, y: y))
                let len = isHour ? tickLineLength : tickLineLength * 0.6
                path.addLine(to: CGPoint(x: baselineX - len, y: y))
            }
            .stroke(isHour ? Color.primary.opacity(0.25) : Color.secondary.opacity(0.2), lineWidth: isHour ? 2 : 1)

            if isHour {
                let labelDate = Calendar.current.date(byAdding: .minute, value: minute, to: baseDate) ?? baseDate
                Text(formatHour(labelDate))
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .position(x: baselineX - tickLineLength - 16, y: y)
            }
        }
    }

    private func formatTime(_ date: Date) -> String {
        let df = DateFormatter()
        df.locale = Locale(identifier: "zh_CN")
        df.dateFormat = "HH:mm"
        return df.string(from: date)
    }

    private func formatHour(_ date: Date) -> String {
        let df = DateFormatter()
        df.locale = Locale(identifier: "zh_CN")
        df.dateFormat = "HH:mm"
        return df.string(from: date)
    }

    private func formatRemaining(_ interval: TimeInterval) -> String {
        let seconds = max(0, Int(interval))
        let h = seconds / 3600
        let m = (seconds % 3600) / 60
        let s = seconds % 60
        if h > 0 {
            return String(format: "%02d:%02d:%02d", h, m, s)
        } else {
            return String(format: "%02d:%02d", m, s)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .preferredColorScheme(.light)
        ContentView()
            .preferredColorScheme(.dark)
    }
}