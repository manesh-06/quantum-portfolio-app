import SwiftUI

struct ContentView: View {
    @State private var tickerInput = "AAPL, MSFT, GOOGL, TSLA, AMZN"
    @State private var useQuantum = true
    @State private var includeBriefing = false
    @State private var result: OptimizeResponse?
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Quantum-Classical Portfolio Engine")
                        .font(.title2).bold()

                    TextField("Tickers, comma separated", text: $tickerInput)
                        .textFieldStyle(.roundedBorder)
                        .autocapitalization(.allCharacters)

                    Toggle("Use quantum randomness (Qiskit)", isOn: $useQuantum)
                    Toggle("Generate AI briefing (slower)", isOn: $includeBriefing)

                    Button(action: runOptimize) {
                        if isLoading {
                            ProgressView()
                        } else {
                            Text("Optimize Portfolio")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isLoading)

                    if let errorMessage = errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.footnote)
                    }

                    if let result = result {
                        Divider()
                        Text("Sharpe Ratio: \(String(format: "%.3f", result.sharpe))")
                            .font(.headline)

                        ForEach(result.tickers, id: \.self) { ticker in
                            VStack(alignment: .leading, spacing: 4) {
                                HStack {
                                    Text(ticker).bold()
                                    Spacer()
                                    Text("\(Int((result.weights[ticker] ?? 0) * 100))%")
                                }
                                HStack(spacing: 12) {
                                    Text("Sentiment: \(result.sentiment[ticker] ?? 0, specifier: "%.2f")")
                                        .foregroundColor((result.sentiment[ticker] ?? 0) >= 0 ? .green : .red)
                                    Text("Cap: \(Int((result.cap[ticker] ?? 0) * 100))%")
                                        .foregroundColor(.secondary)
                                }
                                .font(.caption)
                            }
                            .padding(.vertical, 4)
                        }

                        if let briefing = result.briefing {
                            Divider()
                            Text("Briefing").font(.headline)
                            Text(briefing).font(.body)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Q-Portfolio")
        }
    }

    private func runOptimize() {
        errorMessage = nil
        isLoading = true
        let tickers = tickerInput
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }

        NetworkManager.optimize(
            tickers: tickers, useQuantum: useQuantum, includeBriefing: includeBriefing
        ) { outcome in
            isLoading = false
            switch outcome {
            case .success(let response):
                result = response
            case .failure(let error):
                errorMessage = "Failed: \(error.localizedDescription)"
            }
        }
    }
}
