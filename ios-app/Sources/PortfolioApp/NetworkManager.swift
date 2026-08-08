import Foundation

final class NetworkManager {
    // Point this at your laptop's local IP while backend runs there,
    // e.g. "http://192.168.1.23:8000". Change per network / USB-tether IP.
    static var baseURL = "http://192.168.1.23:8000"

    static func optimize(
        tickers: [String],
        useQuantum: Bool = true,
        includeBriefing: Bool = false,
        completion: @escaping (Result<OptimizeResponse, Error>) -> Void
    ) {
        guard let url = URL(string: "\(baseURL)/portfolio/optimize") else {
            completion(.failure(URLError(.badURL)))
            return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 120 // HHO + FinBERT + RSS can take a while on CPU

        let body = OptimizeRequestBody(
            tickers: tickers, use_quantum: useQuantum, include_briefing: includeBriefing
        )
        request.httpBody = try? JSONEncoder().encode(body)

        URLSession.shared.dataTask(with: request) { data, _, error in
            if let error = error {
                DispatchQueue.main.async { completion(.failure(error)) }
                return
            }
            guard let data = data else {
                DispatchQueue.main.async { completion(.failure(URLError(.badServerResponse))) }
                return
            }
            do {
                let decoded = try JSONDecoder().decode(OptimizeResponse.self, from: data)
                DispatchQueue.main.async { completion(.success(decoded)) }
            } catch {
                DispatchQueue.main.async { completion(.failure(error)) }
            }
        }.resume()
    }
}
