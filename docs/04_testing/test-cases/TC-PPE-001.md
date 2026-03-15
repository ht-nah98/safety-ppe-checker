# Test Cases: Demo Scenarios

> **Module**: Full System
> **Linked Strategy**: [Test Strategy](../test-strategy.md)
> **Total TCs**: 10

---

## 1. Computer Vision (CV) Test Cases

### TC-CV-001: Perfect Pass Scenario
* **Goal**: Verify system detects all 5 PPE classes correctly in ideal conditions.
* **Input**: `demo_pass_001.jpg` (Full body, all PPE on).
* **Steps**:
    1. Upload image via web interface.
    2. Wait for processing.
* **Expected Result**:
    * `overall_pass`: true
    * All 5 items (helmet, vest, gloves, boots, glasses): detected = true.
    * Confidence scores > 0.8.

### TC-CV-002: Missing Helmet (Critical Fail)
* **Goal**: Verify detection of missing primary PPE.
* **Input**: Image worker with vest and gloves but NO helmet.
* **Expected Result**:
    * `overall_pass`: false
    * `helmet`: detected = false (or confidence < 0.5).
    * Results page highlights "THIẾU MŨ BẢO HỘ" in red.

### TC-CV-003: Multiple Missing Items
* **Goal**: Verify checklist updates correctly for multiple violations.
* **Input**: Worker with only helmet and vest (missing gloves, boots, glasses).
* **Expected Result**:
    * `overall_pass`: false
    * `gloves`, `boots`, `glasses`: all detected = false.
    * Checklist shows 2 GREEN, 3 RED marks.

---

## 2. Web Interface (WEB) Test Cases

### TC-WEB-001: Drag & Drop Upload
* **Goal**: Verify usability of file upload.
* **Input**: Valid `.png` file.
* **Steps**: Drag file from desktop to upload zone.
* **Expected Result**: Preview image shows up immediately before clicking "Check".

### TC-WEB-002: Camera Capture
* **Goal**: Verify hardware integration.
* **Steps**:
    1. Click "Camera" mode.
    2. Allow browser permission.
    3. Click "Capture".
* **Expected Result**: High-quality still frame captured and ready for analysis.

### TC-WEB-003: Mobile Responsive Check
* **Goal**: Verify UI on tablet/small screen.
* **Steps**: Open dev tools, set to iPad Mini.
* **Expected Result**: Result cards stack vertically, text remains readable, images resize correctly.

---

## 3. Integration & Dashboard Test Cases

### TC-INT-001: History Sync
* **Goal**: Verify end-to-end data saving.
* **Steps**: Run successful check -> Go to Dashboard.
* **Expected Result**: The latest check appears at the top of the history list with correct timestamp.

### TC-INT-002: Statistics Accuracy
* **Goal**: Verify data aggregation logic.
* **Steps**: Run 2 PASS and 1 FAIL checks.
* **Expected Result**: Dashboard shows "Total: 3", "Pass: 2 (66%)", "Fail: 1 (33%)".

---

## 4. Error Handling (EH) Test Cases

### TC-EH-001: Invalid File Type
* **Goal**: Verify system robustness.
* **Input**: `document.pdf`.
* **Expected Result**: Toast notification or Error message: "Định dạng file không hỗ trợ. Vui lòng upload ảnh (JPG, PNG)".

### TC-EH-002: Connection Timeout
* **Goal**: Handling slow network.
* **Steps**: Set network to "Slow 3G" in DevTools.
* **Expected Result**: Loading spinner shows clearly, user knows system is working, no blank page.
