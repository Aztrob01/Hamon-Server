#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0A00 // defines SDK as W10 version
#endif

#include <windows.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <ctime>
#include "nlohmann/json.hpp"

using json = nlohmann::json;

double Calculate()
{
    static FILETIME prevIdle, prevKernel, prevUser;
    FILETIME idle, kernel, user;
    if (!GetSystemTimes(&idle, &kernel, &user))
    {
        std::cout << "Erorr trying to fetch 'GetSystemTimes'\n";
        return -1.0;
    }

    ULARGE_INTEGER idleTime, kernelTime, userTime;
    ULARGE_INTEGER prevIdleTime, prevKernelTime, prevUserTime;

    idleTime.HighPart = idle.dwHighDateTime;
    kernelTime.HighPart = kernel.dwHighDateTime;
    userTime.HighPart = user.dwHighDateTime;
    idleTime.LowPart = idle.dwLowDateTime;
    kernelTime.LowPart = kernel.dwLowDateTime;
    userTime.LowPart = user.dwLowDateTime;

    prevIdleTime.HighPart = prevIdle.dwHighDateTime;
    prevKernelTime.HighPart = prevKernel.dwHighDateTime;
    prevUserTime.HighPart = prevUser.dwHighDateTime;
    prevIdleTime.LowPart = prevIdle.dwLowDateTime;
    prevKernelTime.LowPart = prevKernel.dwLowDateTime;
    prevUserTime.LowPart = prevUser.dwLowDateTime;

    ULONGLONG idleDelta = idleTime.QuadPart - prevIdleTime.QuadPart;
    ULONGLONG kernelDelta = kernelTime.QuadPart - prevKernelTime.QuadPart;
    ULONGLONG userDelta = userTime.QuadPart - prevUserTime.QuadPart;
    ULONGLONG total = kernelDelta + userDelta;

    double usage = (total - idleDelta) * 100.0 / total;

    prevIdle = idle;
    prevKernel = kernel;
    prevUser = user;

    return usage;
}

int main()
{

    // std::cout << "You can see the results on './output/data.json'";
    while (true)
    {
        int sleepValue = 500;
        time_t timestamp = time(NULL);
        char *now = ctime(&timestamp);
        Sleep(500);
        json jsonText = {
            {"name", "Hamon Live Server -> main.cpp / data.json"},
            {"cpu", Calculate()},
            {"timestamp", now},
            {"interval", sleepValue},
            {"directX", "None"},
            {"gpuname", "None"},
            {"gpu", "None"},
        };

        std::ofstream file("data.json");
        if (file.is_open())
        {
            file << jsonText.dump(4);
            file.close();
        }
    }
}
