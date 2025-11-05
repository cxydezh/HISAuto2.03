from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json
from NetworkUtils.data_display import get_ai_suit_list, get_ai_workflow_by_func_list_id, get_departments, get_patient_ai_result, get_ai_functions, get_ai_workflow, get_ai_hierarchy_list, get_ai_actions_by_group_id
from NetworkUtils.database import db
from main import handle_login

app = Flask(__name__)
app.secret_key = 'his_auto_secret_key_2024'

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空！'})
            
        try:
            # 调用登录成功回调函数
            success_login, is_super_user = handle_login(username, password)
            if success_login:
                # 登录成功，设置会话
                session['logged_in'] = True
                session['username'] = username
                session['is_super_user'] = is_super_user
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            else:
                return jsonify({'success': False, 'message': '用户名或密码错误'})
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/departments')
@login_required
def api_departments():
    departments = get_departments()
    return jsonify(departments)

# 患者数据现在由前端通过Excel文件导入，不再需要后端API
# @app.route('/api/patients/<department>') 已删除
# @app.route('/api/patient/<patient_id>') 已删除

@app.route('/api/ai-functions')
@login_required
def api_ai_functions():
    ai_functions = get_ai_functions()
    return jsonify(ai_functions)

@app.route('/api/ai-suit-list')
@login_required
def api_ai_suit_list():
    ai_suit_list = get_ai_suit_list()
    return jsonify(ai_suit_list)

@app.route('/api/ai-workflow/<function_name>')
@login_required
def api_ai_workflow(function_name):
    workflow = get_ai_workflow(function_name)
    return jsonify(workflow)

@app.route('/api/run-ai', methods=['POST'])
@login_required
def api_run_ai():
    data = request.get_json()
    function_name = data.get('function_name')
    mode = data.get('mode', 'single')
    patient_id = data.get('patient_id')
    func_list_id = data.get('func_list_id')
    
    # 模拟AI运行过程
    workflow =get_ai_workflow_by_func_list_id(func_list_id)
    # workflow = get_ai_workflow(function_name)
    if not workflow:
        return jsonify({'success': False, 'message': '未找到指定的AI功能'})
    
    # 患者信息现在由前端管理，不再从服务器获取
    # 如果前端传递了患者信息，可以使用，否则使用默认值
    patient_name = data.get('patient_name', '未知患者')
    patient_ai_result = get_patient_ai_result(patient_id,func_list_id)
    # 生成模拟的运行结果
    if patient_ai_result:
        run_result = patient_ai_result
    else:
        run_result = f'AI功能 "{function_name}" 运行完成，模式：{mode}'
    
    # 保存到数据库
    import json
    workflow_json = json.dumps(workflow, ensure_ascii=False)
    
    # 调试信息：检查要保存的数据
    print(f"要保存的AI结果数据: {run_result}")
    print(f"数据类型: {type(run_result)}")
    print(f"数据长度: {len(run_result) if run_result else 0}")
    
    db.save_ai_result(
        patient_id=patient_id or 'unknown',
        patient_name=patient_name,
        ai_function=function_name,
        run_mode=mode,
        run_status='完成',
        run_result=run_result,
        workflow_data=workflow_json
    )
    
    # 返回模拟的运行结果
    result = {
        'success': True,
        'workflow': workflow,
        'result': run_result
    }
    
    return jsonify(result)

@app.route('/api/patient-ai-results/<patient_id>')
@login_required
def api_patient_ai_results(patient_id):
    """获取指定患者的AI运行结果列表"""
    results = db.get_patient_ai_results(patient_id)
    return jsonify(results)

@app.route('/api/ai-result-detail/<result_id>')
@login_required
def api_ai_result_detail(result_id):
    """获取AI运行结果详情"""
    result = db.get_ai_result_detail(result_id)
    if result:
        # 调试信息：检查从数据库检索的数据
        print(f"从数据库检索的AI结果数据: {result['run_result']}")
        print(f"数据类型: {type(result['run_result'])}")
        print(f"数据长度: {len(result['run_result']) if result['run_result'] else 0}")
        return jsonify(result)
    else:
        return jsonify({'error': '未找到指定的运行结果'}), 404

@app.route('/api/ai-hierarchy-list/<suit_type>')
@login_required
def api_ai_hierarchy_list(suit_type):
    """获取AI功能列表（从actions_group_hierarchy表）
    
    suit_type: 'personal'（个人）、'department'（科室）、'global'（全局）
    """
    try:
        result_list = get_ai_hierarchy_list(suit_type)
        return jsonify(result_list)
    except Exception as e:
        print(f"获取AI功能列表时出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-actions/<group_id>')
@login_required
def api_ai_actions(group_id):
    """获取指定行为组下所有 action_type 为 'AI' 的记录
    
    group_id: 行为组ID
    """
    try:
        result_list = get_ai_actions_by_group_id(int(group_id))
        return jsonify(result_list)
    except Exception as e:
        print(f"获取AI动作列表时出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 