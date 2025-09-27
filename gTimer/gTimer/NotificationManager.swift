import Foundation
import UserNotifications

enum NotificationManager {
    static let countdownIdentifier = "gTimerCountdown"

    static func requestAuthorization() {
        let center = UNUserNotificationCenter.current()
        center.requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }

    static func scheduleCountdown(after seconds: TimeInterval, title: String = "计时到", body: String = "倒计时结束") {
        guard seconds > 0 else { return }
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: [countdownIdentifier])

        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: seconds, repeats: false)
        let request = UNNotificationRequest(identifier: countdownIdentifier, content: content, trigger: trigger)
        center.add(request) { _ in }
    }
}