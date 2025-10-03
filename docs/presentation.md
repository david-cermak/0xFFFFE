---
marp: true
theme: default
paginate: true
header: 'Practical intro into fuzz-testing'
footer: '0xFFFFE - Fuzzing Fundamentals For Firmware Engineers'
style: |
  h4 {
    font-size: 1.2em;
  }
  pre {
    font-size: 0.8em;
  }
---

# Practical intro into fuzz-testing

![fuzzing](fuzz-intro.jpg)

**David Cermak, Embedded developer**

---

# 0xFFFFE

### __github.com/david-cermak/0xFFFFE__

* **Projects** (demo apps -> libs)
* **Tools** -- fuzzers
  * Black-box
  * Grey box (Coverage guided, state guided, protocol fuzzers, LLM enhanced)
  * White box fuzzers
* **Methods** (Host tests, HW in the loop, QEMU)

---
# Experiment

* mDNS library
  - real library
  - real bug

---


# What is Fuzzing?

> **Dynamic testing technique** that feeds random/malformed input to find crashes, vulnerabilities, and edge cases

## Why Should We Care
- **Robustness**: Find subtle bugs before deployment
- **Security**: Discover vulnerabilities in protocol stacks
- **Edge Cases**: Uncover hard-to-reproduce issues
- **CI Integration**: Automated testing for continuous quality

---

## Fuzzing Approaches

### Black-box (radamsa)

### Grey box fuzzers

* Coverage guided (AFL++)
* State guided, protocol fuzzers (AFLNet)
* LLM enhanced

### White box (angr)

---

## Black box

![fuzzing](black.png)

---

## Grey box

![fuzzing](grey.png)

---

## White box

![fuzzing](white.png)

---


# Fuzzing Approaches

| Approach | Tool | Method | Pros | Cons |
|----------|------|--------|------|------|
| **Black-box** | radamsa | Random input mutation | Simple, fast setup | Limited coverage |
| **Grey-box** | AFL++ | Feedback-driven exploration | High effectiveness, finds complex bugs | Requires instrumentation |
| **White-box** | angr | Path analysis without execution | Works on binaries, deep analysis | Limited, research-focused |

---



# Hello World with radamsa

```cpp
printf("Hello ");
printf(argv[1]);  // printf("%s", argv[1]);
printf("!\n");
// ./hello Josef
// ./hello %s
```

```bash
echo "David @#$^%&" | radamsa -n 1000 | xarg -0 ./hello
#
# 1000 runs, 6 errors found
# AddressSanitizer: SEGV on format string vulnerability
```

- 💡Random inputs ➡️ Use fuzzers to mutate inputs
- 💡Sanitizers ➡️ Address sanitizer caught the issue

---

# Tools and examples

|   |   |     |
|-------------------|------|----|
| **00_radamsa_hello**  | **01_radamsa_sample** |  **02_afl_lwip_dhcp** |
| **03_boofuzz_iotparser** |  **04_boofuzz_mdns** | **05_fuzztest_iotparser** <br/> 💡Property based  <br/> ➡️ Define *correct*|
| **06_angr_firmwarebin** |  **07_afl_lwip** | **08_afl_mdns_gcov** <br/>💡Generate seeds  <br/> ➡️ LLM with gcov |
| **09_aflnet_dhcp_server** | **10_afl_mqtt** | **11_afl_dpcp_server**    |


---

# Experiment: mDNS library

* Explore crashes
* Recreate UDP packet from bin payload
* Send the packet

---

### 💡Start fuzzing now
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  ➡️ Pull __aflplusplus__ docker image
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  ➡️ Generate fuzz targets with coding assistants

### 💡Generate input seed

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ➡️ Use mutators instead of random inputs
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ➡️ Use LLMs, coverage driven

### 💡Next steps
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ➡️ Use sanitizers (asan, uban, ...)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ➡️ Add fuzzing to CI  10m ~ 1h, weekend runs
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ➡️ Integrate with unit/property based tests

---

# Property-based testing integration

```cpp
TEST(IoTParserTest, FuzzMqttTopicParsing) {
  // Combines:
  //   1) unit tests 
  //   2) property based tests
  //   3) fuzzing
  // 16,984 runs, 192 edges covered
  // Found buffer overflow in 69-byte input
}
```
---

# Resources & Next Steps

## 📚 **Learn More**
- **0xFFFFE Repository**: https://github.com/david-cermak/0xFFFFE
- **AFL++ Documentation**: https://github.com/AFLplusplus/AFLplusplus
- **Fuzztest Guide**: https://github.com/google/fuzztest

---
---
---

# Example 4: Firmware Binary with angr
## White-box analysis - Research frontier

```python
# Symbolic execution of firmware binary
# Path analysis without execution
# Limited but powerful for specific cases
```

**Key Takeaways:**
- ✅ **Binary analysis** - no source code needed
- ✅ **Deep exploration** - symbolic path solving
- ⚠️ **Limited scope** - research tool, not production
- ⚠️ **Complex setup** - requires expertise

---

# My Quick Recommendations

## 🚀 **For Fast Results**: AFL++
- Minimal setup, maximum impact
- Coverage-guided exploration
- Works great with embedded protocols

## 🔍 **For Test Integration**: Fuzztest
- Combines with unit testing
- Property-based validation
- Perfect for CI/CD pipelines

---

# Embedded-Specific Considerations

## Environment Options
- **Host testing**: Fast, easy debugging
- **QEMU emulation**: Hardware-like behavior
- **Hardware-in-loop**: Real target validation

## Target Selection
- **Protocol stacks**: DHCP, mDNS, MQTT
- **Parsers**: JSON, HTTP, custom formats
- **Network services**: Servers, clients


---

# Getting Started Workflow

- Start with simple parsers or protocol handlers
- Compile on host
- Setup fuzz target
- Run in CI

---

# CI Integration Strategy

## Continuous Fuzzing Pipeline
```yaml
fuzz_job:
  - Build with AFL++ instrumentation
  - Run fuzzer for 15-60 minutes
  - Check for crashes and timeouts
  - Fail the job if any + upload artifacts
```

---


# Key Takeaways

## **AFL++**

## **Fuzztest**

## **CI integration**

---

# Resources & Next Steps

## 📚 **Learn More**
- **0xFFFFE Repository**: https://github.com/your-repo
- **AFL++ Documentation**: https://github.com/AFLplusplus/AFLplusplus
- **Fuzztest Guide**: https://github.com/google/fuzztest

---

## 🛠️ **Try It Yourself**
1. Clone the 0xFFFFE repository
2. Start with `examples/00_radamsa_hello`
3. Progress to `examples/02_afl_lwip_dhcp`
4. Experiment with `examples/05_fuzztest_iotparser`

---

# Thank You!

**Fuzzing is not just for security professionals**  
**Every embedded engineer should be aware of these techniques**
**0xFFFFE - Fuzzing Fundamentals For Firmware Engineers**
