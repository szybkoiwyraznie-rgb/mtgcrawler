// Optional offline headless instrumentation for the pinned Linux-only research build.
// No web/debugger listener is opened by this code. Not a production emulator feature.
#pragma once
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <unistd.h>
#include <vector>
#include "Core/HLE/sceCtrl.h"
#include "Core/HLE/sceDisplay.h"
#include "Core/MemMap.h"

struct OfflineResearchEvent {
    double start, end;
    unsigned int mask;
};

class OfflineResearch {
public:
    void Start() {
        const char *schedule = std::getenv("PPSSPP_RESEARCH_SCHEDULE");
        const char *prefix = std::getenv("PPSSPP_RESEARCH_VRAM_PREFIX");
        if (!schedule && !prefix) return;
        if (prefix) {
            if (std::strlen(prefix) > 3000 || !*prefix) Fail("invalid capture prefix");
            prefix_ = prefix;
        }
        if (schedule) {
            FILE *f = std::fopen(schedule, "r");
            if (!f) Fail("cannot open schedule");
            char line[512];
            double previousEnd = 0;
            const unsigned int allowed = CTRL_CIRCLE | CTRL_CROSS | CTRL_TRIANGLE | CTRL_SQUARE |
                CTRL_UP | CTRL_DOWN | CTRL_LEFT | CTRL_RIGHT | CTRL_START | CTRL_SELECT |
                CTRL_LTRIGGER | CTRL_RTRIGGER;
            while (std::fgets(line, sizeof(line), f)) {
                if (!std::strchr(line, '\n') && !std::feof(f)) Fail("schedule line too long");
                if (line[0] == '#' || line[0] == '\n') continue;
                double start, duration;
                unsigned int mask;
                char extra;
                if (std::sscanf(line, "%lf %x %lf %c", &start, &mask, &duration, &extra) != 3 ||
                    !std::isfinite(start) || !std::isfinite(duration) || start < previousEnd ||
                    duration <= 0 || duration > 10 || start > 3600 || !mask || (mask & ~allowed) ||
                    events_.size() >= 1000)
                    Fail("invalid or overlapping schedule event");
                events_.push_back({start, start + duration, mask});
                previousEnd = start + duration;
            }
            if (std::ferror(f)) Fail("cannot read schedule");
            std::fclose(f);
        }
        start_ = time_now_d();
        enabled_ = true;
        std::fprintf(stderr, "Offline research enabled: %zu input events, capture=%s\n",
                     events_.size(), prefix_.empty() ? "off" : "on");
    }

    void Step() {
        if (!enabled_) return;
        double elapsed = time_now_d() - start_;
        if (held_ && elapsed >= heldUntil_) {
            __CtrlUpdateButtons(0, held_);
            held_ = 0;
        }
        while (next_ < events_.size() && elapsed >= events_[next_].start) {
            const auto &e = events_[next_++];
            if (elapsed >= e.end) {
                std::fprintf(stderr, "Offline research: missed input at %.2f\n", e.start);
                continue;
            }
            __CtrlUpdateButtons(e.mask, 0);
            held_ = e.mask;
            heldUntil_ = e.end;
            std::fprintf(stderr, "Offline research: input 0x%x at %.2f\n", held_, elapsed);
        }
        if (!prefix_.empty() && captures_ < 100 && elapsed >= captures_ * 2.0) {
            const unsigned int size = 512 * 272 * 2;
            for (unsigned int addr : {0x04000000u, 0x04044000u}) {
                if (!Memory::IsValidRange(addr, size)) Fail("VRAM outside emulated memory");
                char suffix[64];
                std::snprintf(suffix, sizeof(suffix), "-%03u-%08x.raw", captures_, addr);
                WriteRaw(suffix, addr, size);
            }
            // Capture the current PSP display address and declared format as
            // an additional candidate. This still is not synchronized to a
            // completed render or proof of what was displayed on screen.
            PSPPointer<u8> active{};
            u32 stride = 0, format = 0;
            __DisplayGetFramebuf(&active, &stride, &format, 0);
            unsigned int address = active.ptr;
            if (address && stride >= 480 && stride <= 4096 && format <= 3) {
                unsigned int bytes = stride * 272 * (format == 3 ? 4 : 2);
                if (Memory::IsValidRange(address, bytes)) {
                    char suffix[96];
                    std::snprintf(suffix, sizeof(suffix), "-%03u-active-%08x-%u-%u.raw",
                                  captures_, address, stride, format);
                    WriteRaw(suffix, address, bytes);
                    std::fprintf(stderr, "Offline research: active addr=%08x stride=%u fmt=%u\n", address, stride, format);
                }
            }
            std::fprintf(stderr, "Offline research: VRAM sample %u at %.2f (unsynchronized)\n", captures_, elapsed);
            ++captures_;
        }
    }

    void Stop() {
        if (held_) __CtrlUpdateButtons(0, held_);
        held_ = 0;
    }

private:
    void WriteRaw(const char *suffix, unsigned int addr, unsigned int size) {
        std::string path = prefix_ + suffix;
        int fd = open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
        if (fd < 0) Fail("cannot create new VRAM output");
        FILE *out = fdopen(fd, "wb");
        if (!out) { close(fd); Fail("cannot open VRAM output"); }
        bool ok = std::fwrite(Memory::GetPointerUnchecked(addr), 1, size, out) == size;
        if (std::fclose(out) != 0 || !ok) Fail("cannot write VRAM output");
    }
    [[noreturn]] static void Fail(const char *why) {
        std::fprintf(stderr, "Offline research: %s\n", why);
        std::exit(2);
    }
    std::vector<OfflineResearchEvent> events_;
    std::string prefix_;
    double start_ = 0, heldUntil_ = 0;
    size_t next_ = 0;
    unsigned int held_ = 0, captures_ = 0;
    bool enabled_ = false;
};
