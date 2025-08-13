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

    // 科室选择
    document.getElementById('department-select').addEventListener('change', function() {
        loadPatientsByDepartment(this.value);
    });

    // AI功能选择
    document.getElementById('ai-selection').addEventListener('change', function() {
        loadAiFuncList(this.value);
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

    function loadPatientsByDepartment(department) {
        fetch(`/api/patients/${department}`)
            .then(response => response.json())
            .then(data => {
                renderPatientList(data);
            });
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
            })
            .catch(error => {
                console.error('加载AI功能失败:', error);
            });
    }
    function renderAiSuitLists(suit_list) {
        const select = document.getElementById('ai-selection');
        select.innerHTML = '<option value="">请选择AI功能</option>';
        
        suit_list.forEach(suit => {
            const option = document.createElement('option');
            option.value = suit;
            option.textContent = suit;
            select.appendChild(option);
        });
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
        loadPatientInfo(patient.id);
        loadPatientAiResults(patient.id);
    }

    function loadPatientInfo(patientId) {
        fetch(`/api/patient/${patientId}`)
            .then(response => response.json())
            .then(data => {
                renderPatientInfo(data);
            });
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
        infoContainer.innerHTML = `
            <div class="patient-details">
                <h3>患者基本信息</h3>
                <div class="info-grid">
                    <div class="info-item"><label>患者姓名:</label><span>${patient.name}</span></div>
                    <div class="info-item"><label>年龄:</label><span>${patient.age}岁</span></div>
                    <div class="info-item"><label>性别:</label><span>${patient.gender}</span></div>
                    <div class="info-item"><label>入院科室:</label><span>${patient.department}</span></div>
                    <div class="info-item"><label>入院时间:</label><span>${patient.admission_date}</span></div>
                    <div class="info-item"><label>入院天数:</label><span>${patient.admission_days}天</span></div>
                    <div class="info-item"><label>主管医生:</label><span>${patient.attending_doctor}</span></div>
                    <div class="info-item"><label>住院医生:</label><span>${patient.resident_doctor}</span></div>
                    <div class="info-item"><label>主治医生:</label><span>${patient.chief_doctor}</span></div>
                    <div class="info-item"><label>备注信息:</label><span>${patient.notes}</span></div>
                </div>
            </div>
        `;
    }

    function loadAiFuncList(suitName) {
        if (!suitName) {
            document.getElementById('ai-tree').innerHTML = '';
            document.getElementById('ai-description-content').innerHTML = '<p class="placeholder-text">请选择AI功能查看详细描述</p>';
            return;
        }

        fetch(`/api/ai-workflow/${encodeURIComponent(suitName)}`)
            .then(response => response.json())
            .then(data => {
                renderAiTree(data);
                renderAiDescription(data.AI_prompt);
            });
    }

    function renderAiTree(func_list_item) {
        const treeContainer = document.getElementById('ai-tree');
        treeContainer.innerHTML = '';

        func_list_item.forEach((item, index) => {
            const treeItem = document.createElement('div');
            const treeItemID = document.createElement('div');
            treeItem.className = 'ai-tree-item';
            
            // 创建显示名称的span元素
            const nameSpan = document.createElement('span');
            nameSpan.textContent = item.func_list_name;
            nameSpan.className = 'ai-tree-item-name';
            
            treeItemID.className = 'ai-tree-item-id';
            treeItemID.textContent = item.func_list_id;
            treeItemID.hidden = true;
            
            treeItem.appendChild(nameSpan);
            treeItem.appendChild(treeItemID);
            treeItem.addEventListener('click', () => selectAiTreeItem(item));
            treeContainer.appendChild(treeItem);
        });
    }

    function selectAiTreeItem(item) {
        document.querySelectorAll('.ai-tree-item').forEach(el => {
            el.classList.remove('selected');
        });
        
        // 找到当前点击的AI功能项元素并添加选中状态
        const currentTarget = event.currentTarget;
        currentTarget.classList.add('selected');
        
        document.getElementById('ai-description-content').innerHTML = `
            <h4>${item.func_list_name}</h4>
            <p>${item.AI_prompt}</p>
        `;
    }

    function renderAiDescription(description) {
        document.getElementById('ai-description-content').innerHTML = `
            <h4>功能描述</h4>
            <p>${description}</p>
        `;
    }

    function runAiFunction() {
        //这里更改为选中的AI-tree
        const selectedFunctionElement = document.querySelector("#ai-tree > div.ai-tree-item.selected");
        if (!selectedFunctionElement) {
            alert('请先选择AI功能');
            return;
        }
        
        const selectedFunction_name = selectedFunctionElement.querySelector('.ai-tree-item-name').textContent;
        const selectedFunction_id = selectedFunctionElement.querySelector('.ai-tree-item-id').textContent;
        
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
        // 获取当前科室的所有患者
        const currentDepartment = document.getElementById('department-select').value;
        
        fetch(`/api/patients/${currentDepartment}`)
            .then(response => response.json())
            .then(patients => {
                if (patients.length === 0) {
                    alert('当前科室没有患者数据');
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
            })
            .catch(error => {
                console.error('获取患者列表失败:', error);
                progressContainer.innerHTML += '<p class="error">❌ 获取患者列表失败</p>';
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

    // 初始化加载
    loadPatientsByDepartment('personal');
    loadAiFunctions();
}); 