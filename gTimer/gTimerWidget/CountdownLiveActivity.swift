import WidgetKit
import SwiftUI
import ActivityKit

@main
struct gTimerWidgetBundle: WidgetBundle {
    var body: some Widget {
        CountdownLiveActivity()
    }
}

struct CountdownLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: CountdownActivityAttributes.self) { context in
            // Lock Screen / Banner
            ZStack {
                ProgressView(value: progress(from: context.state))
                    .progressViewStyle(.linear)
                HStack {
                    Text(timeString(remaining: context.state.remainingSeconds))
                        .monospacedDigit()
                        .font(.title3)
                    Spacer()
                    Text(endString(date: context.state.endDate))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .padding()
        } dynamicIsland: { context in
            DynamicIsland {
                // Expanded
                DynamicIslandExpandedRegion(.leading) {
                    Text("剩余")
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(timeString(remaining: context.state.remainingSeconds))
                        .monospacedDigit()
                        .font(.title3)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    ProgressView(value: progress(from: context.state))
                        .progressViewStyle(.linear)
                }
            } compactLeading: {
                Text(shortTimeString(remaining: context.state.remainingSeconds))
                    .monospacedDigit()
            } compactTrailing: {
                Image(systemName: "timer")
            } minimal: {
                Text(minimalString(remaining: context.state.remainingSeconds))
            }
        }
    }

    private func progress(from state: CountdownActivityAttributes.ContentState) -> Double {
        let total = max(1, Int(state.endDate.timeIntervalSinceNow) + state.remainingSeconds)
        let clamped = max(0, min(state.remainingSeconds, total))
        return 1.0 - Double(clamped) / Double(total)
    }

    private func timeString(remaining: Int) -> String {
        let h = remaining / 3600
        let m = (remaining % 3600) / 60
        let s = remaining % 60
        if h > 0 { return String(format: "%d:%02d:%02d", h, m, s) }
        return String(format: "%02d:%02d", m, s)
    }

    private func shortTimeString(remaining: Int) -> String {
        let m = remaining / 60
        return String(format: "%dm", m)
    }

    private func minimalString(remaining: Int) -> String {
        let m = remaining / 60
        return String(m)
    }

    private func endString(date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .none
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}