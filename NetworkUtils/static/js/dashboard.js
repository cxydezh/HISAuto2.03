// 工作台页面JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Tab切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });

    // 面板切换
    document.querySelectorAll('.panel-tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const panelName = this.dataset.panel;
            switchPanel(panelName);
        });
    });

    // 更新Excel文件按钮
    document.getElementById('update-excel-btn').addEventListener('click', function() {
        updateExcelFile();
    });

    // 科室选择（已禁用后端加载，改为本地数据过滤）
    document.getElementById('department-select').addEventListener('change', function() {
        // 如果需要按科室过滤，可以在这里实现
        // 目前所有患者数据都在本地，可以直接渲染
        if (window.patientData && window.patientData.length > 0) {
            renderPatientList(window.patientData);
        }
    });

    // AI功能选择
    document.getElementById('ai-selection').addEventListener('change', function() {
        const suitType = this.value;
        if (suitType === 'personal' || suitType === 'department' || suitType === 'global') {
            loadAiFuncList(suitType);
        } else {
            document.getElementById('ai-tree').innerHTML = '';
            document.getElementById('ai-description-content').innerHTML = '<p class="placeholder-text">请选择AI功能查看详细描述</p>';
        }
    });

    // 运行AI按钮
    document.getElementById('run-ai-btn').addEventListener('click', function() {
        runAiFunction();
    });

    function switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
    }

    function switchPanel(panelName) {
        document.querySelectorAll('.panel-tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-panel="${panelName}"]`).classList.add('active');
        document.querySelectorAll('.panel-panel').forEach(panel => panel.classList.remove('active'));
        document.getElementById(`${panelName}-panel`).classList.add('active');
    }

    // 前端患者数据存储
    window.patientData = [];

    // 更新Excel文件函数（在DOMContentLoaded内部定义，通过事件监听器调用）
    function updateExcelFile() {
        // 触发文件选择
        const fileInput = document.getElementById('excel-file-input');
        if (!fileInput) {
            console.error('找不到文件输入框');
            return;
        }
        
        // 清除之前的事件监听器，避免重复绑定
        fileInput.onchange = null;
        
        // 设置新的文件选择处理函数
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (!file) {
                return;
            }
            
            // 检查文件类型
            if (!file.name.match(/\.(xlsx|xls)$/i)) {
                alert('请选择Excel文件（.xlsx或.xls格式）');
                // 重置文件输入
                fileInput.value = '';
                return;
            }
            
            // 读取Excel文件
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    
                    // 获取第一个工作表
                    if (workbook.SheetNames.length === 0) {
                        alert('Excel文件没有工作表');
                        return;
                    }
                    
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    
                    // 转换为JSON格式
                    const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
                    
                    if (jsonData.length === 0) {
                        alert('Excel文件为空，没有数据可导入');
                        return;
                    }
                    
                    // 处理Excel数据，转换为患者列表格式
                    const patients = processExcelData(jsonData);
                    
                    if (patients.length === 0) {
                        alert('Excel文件中没有有效的患者数据');
                        return;
                    }
                    
                    // 更新前端患者数据
                    window.patientData = patients;
                    
                    // 渲染患者列表
                    renderPatientList(patients);
                    
                    alert(`成功导入 ${patients.length} 条患者数据`);
                } catch (error) {
                    console.error('读取Excel文件失败:', error);
                    alert('读取Excel文件失败，请检查文件格式是否正确：' + error.message);
                } finally {
                    // 重置文件输入，允许重复选择同一文件
                    fileInput.value = '';
                }
            };
            
            reader.onerror = function(e) {
                console.error('文件读取错误:', e);
                alert('文件读取失败，请重试');
                fileInput.value = '';
            };
            
            reader.readAsArrayBuffer(file);
        };
        
        // 触发文件选择对话框
        fileInput.click();
    }
    
    function processExcelData(jsonData) {
        // 将Excel数据转换为患者列表格式
        const patients = [];
        
        jsonData.forEach((row, index) => {
            // 尝试识别不同的列名格式
            const patientId = row['patient_id'] || row['Patient ID'] || row['病历号'] || row['id'] || row['ID'] || '';
            const patientName = row['patient_name'] || row['Patient Name'] || row['患者姓名'] || row['name'] || row['姓名'] || '';
            const admissionDate = row['in_hospital_time'] || row['In Hospital Time'] || row['入院时间'] || row['入院日期'] || row['admission_date'] || '';
            
            // 如果缺少关键信息，跳过该行
            if (!patientId && !patientName) {
                console.warn(`第 ${index + 2} 行缺少患者ID和姓名，跳过`);
                return;
            }
            
            const patient = {
                id: String(patientId || `TEMP_${index}`),
                name: String(patientName || '未知'),
                admission_date: formatExcelDate(admissionDate) || new Date().toLocaleDateString('zh-CN'),
                age: row['patient_age'] || row['Patient Age'] || row['年龄'] || row['age'] || '',
                gender: row['patient_gender'] || row['Patient Gender'] || row['性别'] || row['gender'] || '',
                department: row['patient_department'] || row['Patient Department'] || row['科室'] || row['department'] || '',
                bed_num: row['patient_bed_num'] || row['Patient Bed Number'] || row['床号'] || row['bed_num'] || '',
                attending_doctor: row['attending_doctor_id'] || row['Attending Doctor'] || row['主治医生'] || '',
                resident_doctor: row['fellow_doctor_id'] || row['Fellow Doctor'] || row['住院医生'] || '',
                chief_doctor: row['resistant_doctor_id'] || row['Resistant Doctor'] || row['实习医生'] || '',
                notes: row['patient_note'] || row['Patient Note'] || row['备注'] || row['note'] || ''
            };
            
            patients.push(patient);
        });
        
        return patients;
    }
    
    function formatExcelDate(dateValue) {
        if (!dateValue) {
            return '';
        }
        
        // 如果是日期对象
        if (dateValue instanceof Date) {
            return dateValue.toLocaleDateString('zh-CN');
        }
        
        // 如果是数字（Excel日期序列号）
        if (typeof dateValue === 'number') {
            // Excel日期从1900年1月1日开始
            const excelEpoch = new Date(1899, 11, 30);
            const date = new Date(excelEpoch.getTime() + dateValue * 24 * 60 * 60 * 1000);
            return date.toLocaleDateString('zh-CN');
        }
        
        // 如果是字符串，尝试解析
        if (typeof dateValue === 'string') {
            // 尝试多种日期格式
            const dateFormats = [
                /(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})/,
                /(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})/
            ];
            
            for (const format of dateFormats) {
                const match = dateValue.match(format);
                if (match) {
                    const year = match[1].length === 4 ? match[1] : match[3];
                    const month = match[1].length === 4 ? match[2] : match[1];
                    const day = match[1].length === 4 ? match[3] : match[2];
                    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                }
            }
        }
        
        return String(dateValue);
    }

    function loadAiFunctions1() {
        fetch('/api/ai-functions')
            .then(response => response.json())
            .then(data => {
                renderAiFunctions(data);
            })
            .catch(error => {
                console.error('加载AI功能失败:', error);
            });
    }
    function loadAiFunctions() {
        fetch('/api/ai-suit-list')
            .then(response => response.json())
            .then(data => {
                renderAiSuitLists(data);
                // 默认加载"个人"功能列表
                loadAiFuncList('personal');
            })
            .catch(error => {
                console.error('加载AI功能失败:', error);
            });
    }
    function renderAiSuitLists(suit_list) {
        const select = document.getElementById('ai-selection');
        select.innerHTML = '<option value="">请选择AI功能类型</option>';
        
        // 将中文转换为对应的英文值
        const suitTypeMap = {
            '个人': 'personal',
            '科室': 'department',
            '全局': 'global'
        };
        
        suit_list.forEach(suit => {
            const option = document.createElement('option');
            option.value = suitTypeMap[suit] || suit;
            option.textContent = suit;
            select.appendChild(option);
        });
        
        // 默认选中"个人"
        const personalOption = select.querySelector('option[value="personal"]');
        if (personalOption) {
            personalOption.selected = true;
        }
    }
            
    function renderAiFunctions1(functions) {
        const select = document.getElementById('ai-selection');
        select.innerHTML = '<option value="">请选择AI功能</option>';
        
        functions.forEach(func => {
            const option = document.createElement('option');
            option.value = func;
            option.textContent = func;
            select.appendChild(option);
        });
    }
    function renderAiFunctions2(functions) {
        const select = document.getElementById('ai-selection');
        select.innerHTML = '<option value="">请选择AI功能</option>';
        
        functions.forEach(func => {
            const option = document.createElement('option');
            option.value = func["func_list_id"];
            option.textContent = func["func_list_name"];
            select.appendChild(option);
        });
    }

    function renderPatientList(patientData) {
        const tbody = document.querySelector('#patient-list tbody');
        tbody.innerHTML = '';

        patientData.forEach(patient => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${patient.id}</td>
                <td>${patient.name}</td>
                <td>${patient.admission_date}</td>
            `;
            row.addEventListener('click', () => selectPatient(patient));
            tbody.appendChild(row);
        });
    }

    function selectPatient(patient) {
        document.querySelectorAll('#patient-list tbody tr').forEach(row => {
            row.classList.remove('selected');
        });
        event.target.closest('tr').classList.add('selected');
        
        // 从本地数据中获取患者信息，不再从服务器加载
        loadPatientInfo(patient);
        loadPatientAiResults(patient.id);
        
        // 获取当前选中的AI功能的行为组ID，并加载AI提示词列表
        loadAiPromptTable(patient);
    }

    function loadPatientInfo(patient) {
        // 直接使用传入的患者对象，不再从服务器获取
        renderPatientInfo(patient);
    }

    function loadPatientAiResults(patientId) {
        fetch(`/api/patient-ai-results/${patientId}`)
            .then(response => response.json())
            .then(data => {
                renderPatientAiResults(data);
            })
            .catch(error => {
                console.error('加载患者AI结果失败:', error);
                renderPatientAiResults([]);
            });
    }

    function renderPatientAiResults(results) {
        const resultList = document.getElementById('result-list');
        
        if (results.length === 0) {
            resultList.innerHTML = `
                <div class="result-placeholder">
                    <p>暂无运行记录</p>
                </div>
            `;
            return;
        }

        resultList.innerHTML = '';
        
        results.forEach(result => {
            const record = document.createElement('div');
            record.className = 'run-record';
            record.dataset.resultId = result.id;
            record.addEventListener('click', () => selectAiResult(result.id));
            
            record.innerHTML = `
                <div class="record-header">
                    <span class="record-function">${result.ai_function}</span>
                    <span class="record-status ${result.run_status === '完成' ? 'success' : 'failed'}">${result.run_status}</span>
                </div>
                <div class="record-details">
                    <span class="record-mode">${result.run_mode === 'single' ? '单项' : '组群'}</span>
                    <span class="record-time">${formatTime(result.run_time)}</span>
                </div>
            `;
            
            resultList.appendChild(record);
        });
    }

    function selectAiResult(resultId) {
        // 移除其他记录的选中状态
        document.querySelectorAll('.run-record').forEach(record => {
            record.classList.remove('selected');
        });
        
        // 添加选中状态
        event.target.closest('.run-record').classList.add('selected');
        
        // 加载结果详情
        loadAiResultDetail(resultId);
    }

    function loadAiResultDetail(resultId) {
        fetch(`/api/ai-result-detail/${resultId}`)
            .then(response => response.json())
            .then(data => {
                renderAiResultDetail(data);
            })
            .catch(error => {
                console.error('加载AI结果详情失败:', error);
            });
    }

        // 配置Markdown渲染器
    function configureMarkdownRenderer() {
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {}
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });
    }

    // 渲染Markdown内容到指定容器
    function renderMarkdownContent(container, content, title = '运行结果') {
        // 配置Markdown渲染器
        configureMarkdownRenderer();
        
        // 渲染Markdown内容
        const markdownContent = content || '';
        const htmlContent = marked.parse(markdownContent);
        
        container.innerHTML = `
            <h4>${title}</h4>
            <div class="result-item">
                <div class="result-content">
                    <div class="markdown-content">${htmlContent}</div>
                </div>
            </div>
        `;
        
        // 高亮代码块
        container.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    function renderAiResultDetail(result) {
        const resultContainer = document.getElementById('ai-result-content');
        
        // 调试信息：检查接收到的数据
        console.log('接收到的AI结果数据:', result);
        console.log('运行结果内容:', result.run_result);
        console.log('运行结果类型:', typeof result.run_result);
        
        // 渲染Markdown内容
        const markdownContent = result.run_result || '';
        console.log('准备渲染的Markdown内容:', markdownContent);
        
        // 检查内容是否包含Markdown标记
        if (markdownContent.includes('#') || markdownContent.includes('##') || markdownContent.includes('```')) {
            console.log('检测到Markdown格式内容');
        } else {
            console.log('未检测到Markdown格式内容');
        }
        
        resultContainer.innerHTML = `
            <h4>运行结果详情</h4>
            <div class="result-item">
                <h5>${result.ai_function}</h5>
                <p><strong>患者:</strong> ${result.patient_name} (${result.patient_id})</p>
                <p><strong>运行模式:</strong> ${result.run_mode === 'single' ? '单项' : '组群'}</p>
                <p><strong>运行状态:</strong> ${result.run_status}</p>
                <p><strong>运行时间:</strong> ${formatTime(result.run_time)}</p>
                <div class="result-content">
                    <strong>运行结果:</strong>
                    <div class="markdown-content">${marked.parse(markdownContent)}</div>
                </div>
            </div>
        `;
        
        // 高亮代码块
        resultContainer.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    function formatTime(timeString) {
        const date = new Date(timeString);
        return date.toLocaleString('zh-CN');
    }

    function renderPatientInfo(patient) {
        const infoContainer = document.getElementById('patient-info');
        
        // 计算入院天数（如果有入院日期）
        let admissionDays = '';
        if (patient.admission_date) {
            try {
                const admissionDate = new Date(patient.admission_date);
                const today = new Date();
                const diffTime = Math.abs(today - admissionDate);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                admissionDays = diffDays;
            } catch (e) {
                admissionDays = '';
            }
        }
        
        infoContainer.innerHTML = `
            <div class="patient-details">
                <h3>患者基本信息</h3>
                <div class="info-grid">
                    <div class="info-item"><label>患者ID:</label><span>${patient.id || ''}</span></div>
                    <div class="info-item"><label>患者姓名:</label><span>${patient.name || ''}</span></div>
                    <div class="info-item"><label>年龄:</label><span>${patient.age ? patient.age + '岁' : ''}</span></div>
                    <div class="info-item"><label>性别:</label><span>${patient.gender || ''}</span></div>
                    <div class="info-item"><label>科室:</label><span>${patient.department || ''}</span></div>
                    <div class="info-item"><label>床号:</label><span>${patient.bed_num || ''}</span></div>
                    <div class="info-item"><label>入院时间:</label><span>${patient.admission_date || ''}</span></div>
                    ${admissionDays ? `<div class="info-item"><label>入院天数:</label><span>${admissionDays}天</span></div>` : ''}
                    <div class="info-item"><label>主治医生:</label><span>${patient.attending_doctor || ''}</span></div>
                    <div class="info-item"><label>住院医生:</label><span>${patient.resident_doctor || ''}</span></div>
                    <div class="info-item"><label>实习医生:</label><span>${patient.chief_doctor || ''}</span></div>
                    <div class="info-item"><label>备注信息:</label><span>${patient.notes || ''}</span></div>
                </div>
            </div>
        `;
    }

    function loadAiFuncList(suitType) {
        if (!suitType || (suitType !== 'personal' && suitType !== 'department' && suitType !== 'global')) {
            document.getElementById('ai-tree').innerHTML = '';
            document.getElementById('ai-description-content').innerHTML = '<p class="placeholder-text">请选择AI功能查看详细描述</p>';
            return;
        }

        fetch(`/api/ai-hierarchy-list/${suitType}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('加载AI功能列表失败:', data.error);
                    document.getElementById('ai-tree').innerHTML = '<div class="ai-tree-placeholder"><p>加载失败</p></div>';
                    document.getElementById('ai-description-content').innerHTML = '<p class="placeholder-text">加载失败</p>';
                    return;
                }
                renderAiHierarchyTree(data);
            })
            .catch(error => {
                console.error('加载AI功能列表失败:', error);
                document.getElementById('ai-tree').innerHTML = '<div class="ai-tree-placeholder"><p>加载失败</p></div>';
                document.getElementById('ai-description-content').innerHTML = '<p class="placeholder-text">加载失败</p>';
            });
    }

    function renderAiHierarchyTree(hierarchyList) {
        const treeContainer = document.getElementById('ai-tree');
        treeContainer.innerHTML = '';

        if (!hierarchyList || hierarchyList.length === 0) {
            treeContainer.innerHTML = '<div class="ai-tree-placeholder"><p>暂无功能列表</p></div>';
            document.getElementById('ai-description-content').innerHTML = '<p class="placeholder-text">请选择AI功能查看详细描述</p>';
            return;
        }

        hierarchyList.forEach((item) => {
            const treeItem = document.createElement('div');
            treeItem.className = 'ai-tree-item';
            treeItem.dataset.id = item.id;
            
            // 创建显示内容的容器
            const itemContent = document.createElement('div');
            itemContent.className = 'ai-tree-item-content';
            
            // 显示ID
            const idDiv = document.createElement('div');
            idDiv.className = 'ai-tree-item-id';
            idDiv.textContent = `ID: ${item.id}`;
            idDiv.style.fontSize = '0.85em';
            idDiv.style.color = '#666';
            
            // 显示group_name
            const nameDiv = document.createElement('div');
            nameDiv.className = 'ai-tree-item-name';
            nameDiv.textContent = item.group_name || '未命名功能';
            
            // 显示group_note（备注）
            if (item.group_note) {
                const noteDiv = document.createElement('div');
                noteDiv.className = 'ai-tree-item-note';
                noteDiv.textContent = `备注: ${item.group_note}`;
                noteDiv.style.fontSize = '0.85em';
                noteDiv.style.color = '#888';
                noteDiv.style.marginTop = '2px';
                itemContent.appendChild(noteDiv);
            }
            
            itemContent.appendChild(idDiv);
            itemContent.appendChild(nameDiv);
            
            treeItem.appendChild(itemContent);
            
            // 添加点击事件
            treeItem.addEventListener('click', function() {
                // 移除其他项的选中状态
                document.querySelectorAll('.ai-tree-item').forEach(el => {
                    el.classList.remove('selected');
                });
                
                // 添加当前项的选中状态
                this.classList.add('selected');
                
                // 显示功能描述
                const description = item.group_note || '暂无备注信息';
                document.getElementById('ai-description-content').innerHTML = `
                    <h4>${item.group_name || '未命名功能'}</h4>
                    <p><strong>ID:</strong> ${item.id}</p>
                    <p><strong>备注:</strong> ${description}</p>
                `;
            });
            
            treeContainer.appendChild(treeItem);
        });
    }

    function renderAiDescription(description) {
        document.getElementById('ai-description-content').innerHTML = `
            <h4>功能描述</h4>
            <p>${description}</p>
        `;
    }

    function loadAiPromptTable(patient) {
        // 获取当前选中的AI功能项
        const selectedFunctionElement = document.querySelector("#ai-tree > div.ai-tree-item.selected");
        
        if (!selectedFunctionElement) {
            // 如果没有选中的AI功能，清空AI提示词表格
            renderAiPromptTable([]);
            return;
        }
        
        // 获取选中的AI功能的行为组ID
        const groupId = selectedFunctionElement.dataset.id;
        
        if (!groupId) {
            console.warn('无法获取AI功能的行为组ID');
            renderAiPromptTable([]);
            return;
        }
        
        // 向服务器发送请求，获取该行为组下所有 action_type 为 "AI" 的记录
        fetch(`/api/ai-actions/${groupId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('加载AI动作列表失败:', data.error);
                    renderAiPromptTable([]);
                    return;
                }
                renderAiPromptTable(data);
            })
            .catch(error => {
                console.error('加载AI动作列表失败:', error);
                renderAiPromptTable([]);
            });
    }

    function renderAiPromptTable(aiActions) {
        const tbody = document.querySelector('#ai-prompt-table tbody');
        if (!tbody) {
            console.error('找不到 ai-prompt-table tbody');
            return;
        }
        
        tbody.innerHTML = '';
        
        if (!aiActions || aiActions.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = '<td colspan="2">暂无AI提示词</td>';
            tbody.appendChild(emptyRow);
            return;
        }
        
        aiActions.forEach(action => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${escapeHtml(action.action_name || '未命名')}</td>
                <td>${escapeHtml(action.ai_illustration || '')}</td>
            `;
            tbody.appendChild(row);
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function runAiFunction() {
        //这里更改为选中的AI-tree
        const selectedFunctionElement = document.querySelector("#ai-tree > div.ai-tree-item.selected");
        if (!selectedFunctionElement) {
            alert('请先选择AI功能');
            return;
        }
        
        const selectedFunction_name = selectedFunctionElement.querySelector('.ai-tree-item-name').textContent;
        // 从dataset中获取ID，或者从显示的ID文本中提取
        const selectedFunction_id = selectedFunctionElement.dataset.id || 
            selectedFunctionElement.querySelector('.ai-tree-item-id')?.textContent?.replace('ID: ', '') || '';
        
        if (!selectedFunction_id) {
            alert('请先选择AI功能');
            return;
        }

        const mode = document.querySelector('input[name="ai-mode"]:checked').value;
        switchPanel('ai-result');
        
        const progressContainer = document.getElementById('ai-progress');
        const resultContainer = document.getElementById('ai-result-content');
        
        progressContainer.innerHTML = '<h4>AI运行进度</h4>';
        resultContainer.innerHTML = '<h4>运行结果</h4>';

        if (mode === 'group') {
            // 组群模式：对所有患者进行批量运行
            runGroupAiFunction(selectedFunction_name, progressContainer, resultContainer,selectedFunction_id);
        } else {
            // 单项模式：对选中患者运行
            runSingleAiFunction(selectedFunction_name, progressContainer, resultContainer,selectedFunction_id);
        }
    }

    function runSingleAiFunction(selectedFunction_name, progressContainer, resultContainer,selectedFunction_id) {
        // 获取当前选中的患者
        const selectedPatient = document.querySelector('#patient-list tbody tr.selected');
        if (!selectedPatient) {
            alert('请先选择患者');
            return;
        }

        const patientId = selectedPatient.cells[0].textContent;
        const patientName = selectedPatient.cells[1].textContent;

        // 调用后端API运行AI功能
        fetch(`/api/run-ai`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                function_name: selectedFunction_name,
                mode: 'single',
                patient_id: patientId,
                patient_name: patientName,  // 传递患者名称
                func_list_id: selectedFunction_id
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 显示工作流程进度，完成后显示结果
                showWorkflowProgress(data.workflow, progressContainer, () => {
                    // 工作流程完成后的回调函数
                    resultContainer.innerHTML = `
                        <h4>运行结果</h4>
                        <div class="result-item">
                            <h5>${selectedFunction_name}</h5>
                            <p><strong>患者:</strong> ${patientName} (${patientId})</p>
                            <p><strong>运行模式:</strong> 单项</p>
                            <p><strong>运行状态:</strong> 完成</p>
                            <div class="result-content">
                                <strong>结果:</strong>
                                <div class="markdown-content">${marked.parse(data.result || '')}</div>
                            </div>
                        </div>
                    `;
                    
                    // 高亮代码块
                    resultContainer.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                    
                    // 重新加载患者的AI结果列表
                    loadPatientAiResults(patientId);
                });
            } else {
                progressContainer.innerHTML += '<p class="error">❌ AI功能运行失败</p>';
                resultContainer.innerHTML += `<p class="error">错误: ${data.message}</p>`;
                addRunRecord(selectedFunction_name, patientName, 'single', '失败');
            }
        })
        .catch(error => {
            console.error('运行AI功能失败:', error);
            progressContainer.innerHTML += '<p class="error">❌ AI功能运行失败</p>';
            resultContainer.innerHTML += '<p class="error">网络错误，请重试</p>';
            addRunRecord(selectedFunction_name, patientName || '未知', 'single', '失败');
        });
    }

    function runGroupAiFunction(selectedFunction_name, progressContainer, resultContainer,selectedFunction_id) {
        // 从本地数据获取所有患者
        const patients = window.patientData || [];
        
        if (patients.length === 0) {
            alert('当前没有患者数据，请先导入Excel文件');
            return;
        }

                progressContainer.innerHTML = '<h4>AI组群运行进度</h4>';
                resultContainer.innerHTML = '<h4>组群运行结果</h4>';

                let completedCount = 0;
                let successCount = 0;
                let failedCount = 0;
                const results = [];

                // 为每个患者运行AI功能
                patients.forEach((patient, index) => {
                    setTimeout(() => {
                        runAiForPatient(patient, selectedFunction_name, selectedFunction_id, (success, result) => {
                            completedCount++;
                            
                            if (success) {
                                successCount++;
                                results.push(`✅ ${patient.name} (${patient.id}): ${result}`);
                                addRunRecord(selectedFunction_name, patient.name, 'group', '完成');
                            } else {
                                failedCount++;
                                results.push(`❌ ${patient.name} (${patient.id}): ${result}`);
                                addRunRecord(selectedFunction_name, patient.name, 'group', '失败');
                            }

                            // 更新进度
                            progressContainer.innerHTML = `
                                <h4>AI组群运行进度</h4>
                                <p>已完成: ${completedCount}/${patients.length}</p>
                                <p>成功: ${successCount} | 失败: ${failedCount}</p>
                            `;

                            // 所有患者处理完成
                            if (completedCount === patients.length) {
                                progressContainer.innerHTML += '<p><strong>🎉 组群运行完成！</strong></p>';
                                
                                resultContainer.innerHTML = `
                                    <h4>组群运行结果</h4>
                                    <div class="result-item">
                                        <h5>${selectedFunction_name} - 组群运行</h5>
                                        <p><strong>总患者数:</strong> ${patients.length}</p>
                                        <p><strong>成功:</strong> ${successCount}</p>
                                        <p><strong>失败:</strong> ${failedCount}</p>
                                        <p><strong>成功率:</strong> ${((successCount / patients.length) * 100).toFixed(1)}%</p>
                                    </div>
                                    <div class="result-details">
                                        <h6>详细结果:</h6>
                                        ${results.map(result => `<p>${result}</p>`).join('')}
                                    </div>
                                `;
                            }
                        });
                    }, index * 1000); // 每个患者间隔1秒开始
                });
    }

    function runAiForPatient(patient, functionName, func_list_id, callback) {
        fetch('/api/run-ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                function_name: functionName,
                mode: 'single',
                patient_id: patient.id,
                patient_name: patient.name,  // 传递患者名称
                func_list_id: func_list_id
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                callback(true, data.result);
            } else {
                callback(false, data.message || '运行失败');
            }
        })
        .catch(error => {
            console.error(`患者 ${patient.name} AI运行失败:`, error);
            callback(false, '网络错误');
        });
    }

    function addRunRecord(functionName, patientName, mode, status) {
        const resultList = document.getElementById('result-list');
        
        // 移除占位符
        const placeholder = resultList.querySelector('.result-placeholder');
        if (placeholder) {
            placeholder.remove();
        }

        const record = document.createElement('div');
        record.className = 'run-record';
        record.innerHTML = `
            <div class="record-header">
                <span class="record-function">${functionName}</span>
                <span class="record-status ${status === '完成' ? 'success' : 'failed'}">${status}</span>
            </div>
            <div class="record-details">
                <span class="record-patient">${patientName}</span>
                <span class="record-mode">${mode === 'single' ? '单项' : '组群'}</span>
                <span class="record-time">${new Date().toLocaleTimeString()}</span>
            </div>
        `;

        // 添加到列表顶部
        resultList.insertBefore(record, resultList.firstChild);
    }

    function showWorkflowProgress(workflow, container, onComplete) {
        let currentStep = 0;
        
        function updateProgress() {
            if (currentStep < workflow.length) {
                const step = workflow[currentStep];
                container.innerHTML += `<p>🔄 ${step.name} - ${step.description}</p>`;
                currentStep++;
                
                // 模拟步骤执行时间
                setTimeout(() => {
                    container.innerHTML = container.innerHTML.replace(
                        `🔄 ${step.name}`,
                        `✅ ${step.name}`
                    );
                    updateProgress();
                }, step.delay );
            } else {
                container.innerHTML += '<p><strong>🎉 所有步骤执行完成！</strong></p>';
                // 工作流程完成后执行回调函数
                if (onComplete && typeof onComplete === 'function') {
                    onComplete();
                }
            }
        }
        
        updateProgress();
    }

    // 初始化加载（不再从服务器加载患者数据）
    // 患者数据将通过Excel文件导入到前端
    // 如果需要默认显示空列表，可以取消下面的注释
    // renderPatientList([]);
    
    loadAiFunctions();
}); 