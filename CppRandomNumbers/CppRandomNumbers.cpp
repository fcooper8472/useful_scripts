#include <algorithm>
#include <random>
#include <vector>
#include <iostream>

template<typename T>
void PrintVector(const std::vector<T>& v)
{
    for(const auto& x : v)
    {
        std::cout << x << std::endl;
    }
}

int main()
{
    // Generate a non-deterministic random seed, and a standard Mersenne twister
    std::random_device rd;
    std::mt19937 gen(rd());

    //////////// Continuous Univariate: Uniform
    {
        const double a = 1.23;
        const double b = 2.34;
        const int n = 25;

        // PDF.  Note support is [a, b) not [a, b].  You can use std::nextafter(b, b + 1.0) if you care
        std::uniform_real_distribution<> dis(a, b);

        // Random sample of size n
        std::vector<double> sample(n);
        std::generate(sample.begin(), sample.end(), [&](){return dis(gen);});
    }

    //////////// Continuous Univariate: Normal
    {
        const double mean = 1.23;
        const double stddev = 0.23;
        const int n = 25;

        // PDF
        std::normal_distribution<> dis(mean, stddev);

        // Random sample of size n
        std::vector<double> sample(n);
        std::generate(sample.begin(), sample.end(), [&](){return dis(gen);});
    }

    //////////// Continuous Univariate: Beta
    {
        const double alpha = 1.23;
        const double beta = 2.34;
        const int n = 5000;

        // No beta distribution in the standard library, so construct samples using two Gammas
        std::gamma_distribution<> dis_alpha(alpha, 1.0);
        std::gamma_distribution<> dis_beta(beta, 1.0);

        // PDF
        auto dis = [&](std::mt19937& g){
            const double X = dis_alpha(gen);
            return X / (X + dis_beta(gen));
        };

        // Random sample of size n
        std::vector<double> sample(n);
        std::generate(sample.begin(), sample.end(), [&](){return dis(gen);});

        PrintVector(sample);
    }
}