# 🚀 AI Interaction Tool - Persistent UI Mode Guide

## 📋 **Overview**

AI Interaction Tool giờ đây hỗ trợ **Persistent UI Mode** - cho phép UI chạy liên tục thay vì popup mỗi khi agent gọi tool.

### 🔄 **New Architecture:**

**Previous (Popup Mode):**
```
Agent Call Tool → UI Popup → User Input → UI Close → Response to Agent
```

**New (Persistent Mode):**
```
Terminal Command → Persistent UI Launch
        ↓
Agent Call Tool → Wait State (no UI popup)
        ↓
User Input (via persistent UI) → Send → Response to Agent → UI Reset (stays open)
        ↓
Ready for next interaction
```

---

## 🛠️ **Setup & Usage**

### 1️⃣ **Launch Persistent UI**

Trong terminal, navigate tới thư mục AI-interaction và chạy:

```bash
# Method 1: Direct script
python main.py --ui

# Method 2: Module mode  
python -m ai_interaction_tool --ui

# Alternative flags
python main.py --persistent
```

**Expected output:**
```
🚀 Launching AI Interaction Tool in Persistent Mode...
📌 UI will stay open for continuous agent communication
💡 Use 'Minimize' button to run in background
⚠️  Keep this terminal open while UI is running
------------------------------------------------------------
```

### 2️⃣ **UI Features**

**Persistent UI có những thay đổi sau:**

- **Window Title**: "AI Interaction Tool - Persistent Mode"
- **Status Indicator**: 
  - 🟢 "Ready for input" - sẵn sàng
  - 🟡 "Agent waiting for input..." - agent đang chờ
- **Close Button**: Thay đổi thành "Minimize" (không đóng app)
- **Auto-Focus**: Tự động focus khi agent call tool

### 3️⃣ **Agent Interaction Flow**

1. **Agent calls ai_interaction tool** → Tool gửi request tới persistent UI
2. **Persistent UI detects request** → Status chuyển yellow, window focus
3. **User nhập message** → Click Send
4. **Response sent to agent** → UI reset, ready for next interaction

---

## ⚡ **Communication Mechanism**

### 📡 **File-Based Bridge**

Tool sử dụng file-based communication trong temp directory:
- **Request file**: Agent → UI signal
- **Response file**: UI → Agent data  
- **Status file**: Current state tracking

### 🔄 **Automatic Fallback**

Nếu Persistent UI không chạy:
- Tool tự động fallback về popup mode
- Không có sự cố, hoạt động bình thường như trước

---

## 🎯 **Benefits**

### ✅ **User Experience:**
- **No interruption**: UI luôn sẵn sàng, không mất context
- **Better workflow**: Không cần chờ popup load
- **Background mode**: Có thể minimize và chạy ngầm
- **Persistent attachments**: Files/images không bị clear

### ✅ **Agent Performance:**
- **Faster response**: Không có UI startup delay
- **Reliable communication**: File-based bridge very stable
- **Backward compatibility**: Old popup mode vẫn hoạt động

---

## 🔧 **Advanced Usage**

### 🎮 **Multiple Modes**

**Persistent Mode (Recommended):**
```bash
python main.py --ui        # Launch persistent UI
# Agent calls tool → communicates with persistent UI
```

**Popup Mode (Legacy):**
```bash
# No persistent UI running
# Agent calls tool → popup dialog (old behavior)
```

### 📁 **Communication Files**

Location: `%TEMP%/ai_interaction_bridge/`
- `request.json` - Agent requests
- `response.json` - UI responses  
- `status.json` - Current state

### 🛡️ **Error Handling**

- **Timeout**: 5 minutes cho user response
- **Cleanup**: Auto cleanup communication files
- **Recovery**: Restart persistent UI nếu có issues

---

## 🚨 **Troubleshooting**

### ❓ **Common Issues**

**Q: UI không hiện khi agent call tool?**
A: Kiểm tra persistent UI có đang chạy không. Restart với `python main.py --ui`

**Q: Agent timeout khi chờ response?**
A: Default timeout là 5 phút. Nhập message và send trong thời gian này.

**Q: UI freeze hoặc không response?**
A: Đóng terminal và restart persistent UI.

**Q: Không thể close UI?**
A: UI chỉ minimize, không close. Dùng Ctrl+C trong terminal để stop.

### 🔧 **Debug Mode**

Check communication status:
```python
from ai_interaction_tool.core.communication_bridge import get_bridge
bridge = get_bridge()
print(bridge.get_status())
```

---

## 📝 **Migration Guide**

### 🔄 **From Old Version**

1. **No config changes needed** - tool tự động detect
2. **Old popup mode vẫn hoạt động** - backward compatible
3. **Gradually switch** - test persistent mode trước

### ⚙️ **Configuration**

All existing config (workspace, attachments, language) được preserve và hoạt động trong persistent mode.

---

## 🎉 **Summary**

**Persistent UI Mode** cung cấp:
- ✅ **Continuous communication channel** 
- ✅ **Better user experience**
- ✅ **Improved performance**
- ✅ **Full backward compatibility**
- ✅ **Easy setup and usage**

**Command để bắt đầu:**
```bash
cd AI-interaction
python main.py --ui
```

Sau đó agent có thể gọi tool bình thường, UI sẽ tự động handle! 🚀
