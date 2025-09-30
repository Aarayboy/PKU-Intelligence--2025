import React, { useState } from 'react';
import {
  BookOpen,
  Upload,
  Download,
  Tag,
  Share2,
  MessageSquare,
  CheckSquare,
  Calendar,
  Clock,
  Plus,
  Search,
  Filter,
  Settings,
  Bell,
  User,
  FileText,
  Folder,
  Star,
  MoreHorizontal
} from 'lucide-react';

const SmartLearningAssistant = () => {
  const [activeTab, setActiveTab] = useState('notes');
  const [notes, setNotes] = useState([
    { id: 1, title: '机器学习基础', category: '人工智能', date: '2025-09-25', starred: true },
    { id: 2, title: '深度学习概念', category: '人工智能', date: '2025-09-24', starred: false },
    { id: 3, title: '数据结构与算法', category: '编程', date: '2025-09-23', starred: true }
  ]);

  const [todos, setTodos] = useState([
    { id: 1, task: '完成机器学习期末项目', completed: false, priority: 'high', dueDate: '2025-09-28', dueTime: '23:59' },
    { id: 2, task: '提交深度学习作业报告', completed: false, priority: 'high', dueDate: '2025-09-29', dueTime: '18:00' },
    { id: 3, task: '准备小组讨论PPT', completed: false, priority: 'high', dueDate: '2025-09-30', dueTime: '15:30' },
    { id: 4, task: '复习线性代数知识点', completed: false, priority: 'medium', dueDate: '2025-10-02', dueTime: '12:00' },
    { id: 5, task: '阅读推荐论文3篇', completed: false, priority: 'medium', dueDate: '2025-10-05', dueTime: '20:00' },
    { id: 6, task: '整理课堂笔记', completed: true, priority: 'medium', dueDate: '2025-09-27', dueTime: '16:00' },
    { id: 7, task: '参加学术讲座', completed: false, priority: 'low', dueDate: '2025-10-08', dueTime: '14:00' },
    { id: 8, task: '更新个人简历', completed: false, priority: 'low', dueDate: '2025-10-10', dueTime: '10:00' }
  ]);

  const [schedule, setSchedule] = useState({
    '周一': ['', '数据结构', '机器学习', '', '深度学习', '', '', ''],
    '周二': ['', '', '算法分析', '小组讨论', '', '人工智能', '', ''],
    '周三': ['', '机器学习', '', '计算机视觉', '', '', '', ''],
    '周四': ['', '', '深度学习', '', '小组项目', '', '', ''],
    '周五': ['', '数据挖掘', '', '', '论文研讨', '', '', '']
  });

  const timeSlots = [
    '08:00-09:00',
    '09:00-10:00',
    '10:00-11:00',
    '11:00-12:00',
    '12:00-13:00',
    '13:00-14:00',
    '14:00-15:00',
    '15:00-16:00'
  ];

  const learningLinks = [
    [
      { id: 1, title: '机器学习', desc: '斯坦福CS229', color: 'from-blue-500 to-purple-500', icon: '🤖', url: '#' },
      { id: 2, title: '深度学习', desc: 'Andrew Ng课程', color: 'from-purple-500 to-pink-500', icon: '🧠', url: '#' },
      { id: 3, title: '计算机视觉', desc: 'CS231n课程', color: 'from-green-500 to-blue-500', icon: '👁️', url: '#' },
      { id: 4, title: 'NLP处理', desc: 'CS224n课程', color: 'from-orange-500 to-red-500', icon: '💬', url: '#' }
    ],
    [
      { id: 5, title: 'LeetCode', desc: '算法刷题', color: 'from-yellow-500 to-orange-500', icon: '⚡', url: '#' },
      { id: 6, title: 'GitHub', desc: '代码仓库', color: 'from-gray-600 to-gray-800', icon: '📦', url: '#' },
      { id: 7, title: 'Stack Overflow', desc: '技术问答', color: 'from-orange-600 to-yellow-500', icon: '❓', url: '#' },
      { id: 8, title: 'Kaggle', desc: '数据竞赛', color: 'from-cyan-500 to-blue-500', icon: '🏆', url: '#' }
    ],
    [
      { id: 9, title: '图书馆', desc: '学术资源', color: 'from-indigo-500 to-purple-500', icon: '📚', url: '#' },
      { id: 10, title: 'arXiv', desc: '学术论文', color: 'from-red-500 to-pink-500', icon: '📄', url: '#' },
      { id: 11, title: 'Google Scholar', desc: '学者搜索', color: 'from-blue-600 to-indigo-600', icon: '🎓', url: '#' },
      { id: 12, title: 'ResearchGate', desc: '研究网络', color: 'from-teal-500 to-cyan-500', icon: '🔬', url: '#' }
    ]
  ];

  const sortTodos = (todos) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };

    return [...todos].sort((a, b) => {
      // 首先按完成状态排序（未完成的在前）
      if (a.completed !== b.completed) {
        return a.completed - b.completed;
      }

      // 对未完成的任务，按优先级排序
      if (!a.completed && !b.completed) {
        if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        }
        // 相同优先级按截止时间排序
        const dateA = new Date(a.dueDate + ' ' + a.dueTime);
        const dateB = new Date(b.dueDate + ' ' + b.dueTime);
        return dateA - dateB;
      }

      return 0;
    });
  };

  const getTimeUrgency = (dueDate, dueTime) => {
    const now = new Date();
    const due = new Date(dueDate + ' ' + dueTime);
    const diffHours = (due - now) / (1000 * 60 * 60);

    if (diffHours < 24) return 'urgent';
    if (diffHours < 72) return 'soon';
    return 'normal';
  };

  const formatTimeRemaining = (dueDate, dueTime) => {
    const now = new Date();
    const due = new Date(dueDate + ' ' + dueTime);
    const diff = due - now;

    if (diff < 0) return '已过期';

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (days > 0) return `${days}天${hours}小时`;
    if (hours > 0) return `${hours}小时`;
    return '不到1小时';
  };

  const toggleStar = (id) => {
    setNotes(notes.map(note =>
        note.id === id ? { ...note, starred: !note.starred } : note
    ));
  };

  const TabButton = ({ id, label, icon: Icon, active, onClick }) => (
      <button
          onClick={() => onClick(id)}
          className={`flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 ${
              active
                  ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                  : 'bg-white/80 text-gray-600 hover:bg-white hover:text-blue-600 hover:shadow-md'
          }`}
      >
        <Icon size={20} />
        <span className="font-medium">{label}</span>
      </button>
  );

  const NoteCard = ({ note }) => (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl p-5 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20 group">
        <div className="flex justify-between items-start mb-3">
          <h3 className="font-semibold text-gray-800 text-lg group-hover:text-blue-600 transition-colors">
            {note.title}
          </h3>
          <button
              onClick={() => toggleStar(note.id)}
              className={`p-1 rounded-full transition-all ${note.starred ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
          >
            <Star size={18} fill={note.starred ? 'currentColor' : 'none'} />
          </button>
        </div>
        <div className="flex items-center justify-between text-sm text-gray-500">
        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
          {note.category}
        </span>
          <span>{note.date}</span>
        </div>
        <div className="mt-4 flex gap-2">
          <button className="flex items-center gap-1 text-blue-600 hover:bg-blue-50 px-3 py-1 rounded-lg transition-colors">
            <Share2 size={14} />
            <span className="text-sm">共享</span>
          </button>
          <button className="flex items-center gap-1 text-green-600 hover:bg-green-50 px-3 py-1 rounded-lg transition-colors">
            <MessageSquare size={14} />
            <span className="text-sm">批注</span>
          </button>
        </div>
      </div>
  );

  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const TodoItem = ({ todo }) => {
    const urgency = getTimeUrgency(todo.dueDate, todo.dueTime);
    const timeRemaining = formatTimeRemaining(todo.dueDate, todo.dueTime);

    return (
        <div className={`bg-white/90 backdrop-blur-sm rounded-xl p-5 shadow-lg border-l-4 transition-all duration-300 ${
            todo.completed
                ? 'opacity-75 border-l-gray-300'
                : urgency === 'urgent'
                    ? 'border-l-red-500 hover:shadow-xl bg-red-50/50'
                    : urgency === 'soon'
                        ? 'border-l-yellow-500 hover:shadow-xl bg-yellow-50/50'
                        : 'border-l-blue-500 hover:shadow-xl'
        } border border-white/20`}>
          <div className="flex items-start gap-4">
            <button
                onClick={() => toggleTodo(todo.id)}
                className={`mt-1 p-2 rounded-lg transition-all ${
                    todo.completed
                        ? 'bg-green-100 text-green-600'
                        : 'bg-gray-100 text-gray-400 hover:bg-green-100 hover:text-green-600'
                }`}
            >
              <CheckSquare size={20} fill={todo.completed ? 'currentColor' : 'none'} />
            </button>

            <div className="flex-1">
              <h4 className={`font-semibold text-lg mb-2 ${
                  todo.completed ? 'line-through text-gray-500' : 'text-gray-800'
              }`}>
                {todo.task}
              </h4>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    todo.priority === 'high'
                        ? 'bg-red-100 text-red-700 border border-red-200'
                        : todo.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                            : 'bg-green-100 text-green-700 border border-green-200'
                }`}>
                  {todo.priority === 'high' ? '🔴 高优先级' : todo.priority === 'medium' ? '🟡 中等' : '🟢 低优先级'}
                </span>
                </div>

                <div className="text-right">
                  <div className={`font-bold text-lg ${
                      urgency === 'urgent'
                          ? 'text-red-600 animate-pulse'
                          : urgency === 'soon'
                              ? 'text-orange-600'
                              : 'text-blue-600'
                  }`}>
                    {todo.dueDate} {todo.dueTime}
                  </div>
                  <div className={`text-sm font-medium ${
                      urgency === 'urgent'
                          ? 'text-red-500'
                          : urgency === 'soon'
                              ? 'text-orange-500'
                              : 'text-gray-500'
                  }`}>
                    {!todo.completed && `⏰ 剩余 ${timeRemaining}`}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    );
  };

  const ScheduleGrid = () => (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 overflow-hidden">
        <div className="grid grid-cols-6 gap-0">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 font-semibold text-center">
            时间/星期
          </div>
          {Object.keys(schedule).map(day => (
              <div key={day} className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 font-semibold text-center">
                {day}
              </div>
          ))}

          {/* Time slots and courses */}
          {timeSlots.map((time, timeIndex) => (
              <React.Fragment key={time}>
                <div className="bg-gray-50 p-3 font-medium text-gray-700 text-sm border-r border-gray-200 flex items-center">
                  {time}
                </div>
                {Object.entries(schedule).map(([day, courses]) => (
                    <div
                        key={`${day}-${timeIndex}`}
                        className={`p-3 border-r border-b border-gray-100 min-h-[60px] flex items-center justify-center text-center transition-all hover:bg-blue-50 ${
                            courses[timeIndex]
                                ? 'bg-blue-100 text-blue-800 font-medium cursor-pointer hover:bg-blue-200'
                                : 'bg-white hover:bg-gray-50'
                        }`}
                    >
                      <span className="text-sm">{courses[timeIndex] || ''}</span>
                    </div>
                ))}
              </React.Fragment>
          ))}
        </div>
      </div>
  );

  const LinkGridCard = ({ link }) => (
      <div
          className="bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20 group cursor-pointer transform hover:scale-105 flex flex-col items-center text-center min-h-[120px] justify-center"
          onClick={() => window.open(link.url, '_blank')}
      >
        <div className={`w-12 h-12 bg-gradient-to-r ${link.color} rounded-lg mb-2 flex items-center justify-center text-white text-xl group-hover:scale-110 transition-transform shadow-md`}>
          {link.icon}
        </div>
        <h3 className="font-semibold text-gray-800 text-sm group-hover:text-blue-600 transition-colors mb-1">{link.title}</h3>
        <p className="text-gray-600 text-xs">{link.desc}</p>
      </div>
  );

  const LinkGrid = ({ links, title }) => (
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {links.map(link => (
              <LinkGridCard key={link.id} link={link} />
          ))}
        </div>
      </div>
  );

  return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl text-white">
                  <BookOpen size={24} />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  智能学习助手
                </h1>
              </div>
              <div className="flex items-center gap-4">
                <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                  <Bell size={20} />
                </button>
                <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                  <Settings size={20} />
                </button>
                <button className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <User size={20} />
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Navigation */}
          <nav className="flex gap-4 mb-8 overflow-x-auto pb-2">
            <TabButton
                id="notes"
                label="笔记管理"
                icon={FileText}
                active={activeTab === 'notes'}
                onClick={setActiveTab}
            />
            <TabButton
                id="links"
                label="学习链接"
                icon={Folder}
                active={activeTab === 'links'}
                onClick={setActiveTab}
            />
            <TabButton
                id="todos"
                label="任务清单"
                icon={CheckSquare}
                active={activeTab === 'todos'}
                onClick={setActiveTab}
            />
            <TabButton
                id="schedule"
                label="课表管理"
                icon={Calendar}
                active={activeTab === 'schedule'}
                onClick={setActiveTab}
            />
          </nav>

          {/* Content */}
          <div className="space-y-6">
            {activeTab === 'notes' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">笔记管理</h2>
                    <div className="flex gap-3">
                      <button className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors shadow-lg">
                        <Upload size={18} />
                        上传笔记
                      </button>
                      <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-lg">
                        <Plus size={18} />
                        新建笔记
                      </button>
                    </div>
                  </div>

                  <div className="mb-6 flex gap-4">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                      <input
                          type="text"
                          //placeholder="搜索笔记..."
                          placeholder="Hello World"

                          className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 backdrop-blur-sm"
                      />
                    </div>
                    <button className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-3 border border-gray-200 rounded-lg hover:bg-white transition-colors">
                      <Filter size={18} />
                      筛选
                    </button>
                    <button className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-3 border border-gray-200 rounded-lg hover:bg-white transition-colors">
                      <Tag size={18} />
                      分类
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {notes.map(note => (
                        <NoteCard key={note.id} note={note} />
                    ))}
                  </div>
                </div>
            )}

            {activeTab === 'links' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">常用学习链接跳转</h2>
                    <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-lg">
                      <Plus size={18} />
                      添加链接
                    </button>
                  </div>

                  <div className="space-y-8">
                    <LinkGrid links={learningLinks[0]} title="📚 在线课程" />
                    <LinkGrid links={learningLinks[1]} title="💻 编程开发" />
                    <LinkGrid links={learningLinks[2]} title="🎓 学术研究" />
                  </div>
                </div>
            )}

            {activeTab === 'todos' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800">任务清单 (To Do List)</h2>
                      <p className="text-gray-600 mt-1">按优先级和截止时间智能排序</p>
                    </div>
                    <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-lg">
                      <Plus size={18} />
                      添加任务
                    </button>
                  </div>

                  <div className="grid gap-4">
                    {sortTodos(todos).map(todo => (
                        <TodoItem key={todo.id} todo={todo} />
                    ))}
                  </div>

                  <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-blue-600 font-semibold">💡 智能提醒</span>
                    </div>
                    <div className="text-sm text-gray-700">
                      <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      24小时内截止
                    </span>
                        <span className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      3天内截止
                    </span>
                        <span className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      时间充裕
                    </span>
                      </div>
                    </div>
                  </div>
                </div>
            )}

            {activeTab === 'schedule' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">课表管理</h2>
                    <div className="flex gap-3">
                      <button className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors shadow-lg">
                        <Upload size={18} />
                        导入Excel
                      </button>
                      <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-lg">
                        <Plus size={18} />
                        添加课程
                      </button>
                    </div>
                  </div>

                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">课程时间表</h3>
                    <ScheduleGrid />
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">小组讨论时间匹配</h3>
                    <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-white/20">
                      <p className="text-gray-600 mb-4">根据所有成员的课表，智能推荐最佳讨论时间：</p>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 text-center">
                          <div className="text-green-600 font-semibold text-lg">周二 14:00-15:00</div>
                          <div className="text-green-700 text-sm mt-2">✓ 最佳推荐</div>
                          <div className="text-xs text-green-600 mt-1">5/5 成员可参加</div>
                        </div>
                        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 text-center">
                          <div className="text-yellow-700 font-semibold text-lg">周四 15:00-16:00</div>
                          <div className="text-yellow-700 text-sm mt-2">次优选择</div>
                          <div className="text-xs text-yellow-600 mt-1">4/5 成员可参加</div>
                        </div>
                        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 text-center">
                          <div className="text-blue-700 font-semibold text-lg">周五 09:00-10:00</div>
                          <div className="text-blue-700 text-sm mt-2">可选时间</div>
                          <div className="text-xs text-blue-600 mt-1">3/5 成员可参加</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            )}
          </div>
        </div>
      </div>
  );
};

export default SmartLearningAssistant;