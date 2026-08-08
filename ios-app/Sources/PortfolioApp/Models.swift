import Foundation

struct OptimizeResponse: Codable {
    let tickers: [String]
    let weights: [String: Double]
    let sharpe: Double
    let sentiment: [String: Double]
    let cap: [String: Double]
    let briefing: String?
}

struct OptimizeRequestBody: Codable {
    let tickers: [String]
    let use_quantum: Bool
    let include_briefing: Bool
}
