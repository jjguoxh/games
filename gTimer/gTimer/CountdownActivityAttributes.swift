import Foundation
import ActivityKit

struct CountdownActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var remainingSeconds: Int
        var endDate: Date
    }

    // Static attributes if needed later (e.g., title)
    var name: String = "计时"
}