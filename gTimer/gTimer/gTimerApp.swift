import SwiftUI

@main
struct gTimerApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .task {
                    NotificationManager.requestAuthorization()
                }
        }
    }
}