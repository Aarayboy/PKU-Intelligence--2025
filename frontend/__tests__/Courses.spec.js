import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Courses from '@/component/views/Courses.vue';

// Mock useNotification 避免真实弹窗/依赖
vi.mock('@/composables/useNotification', () => ({
  useNotification: () => ({ setNotification: vi.fn() }),
}));

// 辅助：创建模拟 userData，接收课程占用的索引数组（0..83）
function makeMockUserData(courseIndices = []) {
  const allCourses = courseIndices.map((idx, i) => ({
    id: `c${i}`,
    name: `Course${i}`,
    teacher: `T${i}`,
    location: `L${i}`,
    times: [idx],
  }));
  // map index -> course
  const indexMap = new Map();
  allCourses.forEach(c => {
    (c.times || []).forEach(t => indexMap.set(t, c));
  });

  return {
    userId: null, // 保证 onMounted 的 loadSchedule 不会调用后端
    courseTable: {
      allCourses,
      getCourseByIndex: (index) => indexMap.get(index) ?? null,
    },
    updateCourseTable: vi.fn(),
  };
}

// 辅助：根据索引数组计算期望的 rowEmpty（12）和 colEmpty（7）
function expectedRowCol(courseIndices) {
  const rowEmpty = Array.from({ length: 12 }, () => true);
  const colEmpty = Array.from({ length: 7 }, () => true);
  courseIndices.forEach(index => {
    if (typeof index !== 'number' || index < 0 || index > 83) return;
    const period = Math.floor(index / 7) + 1; // 1..12
    const dayIdx = index % 7; // 0..6
    rowEmpty[period - 1] = false;
    colEmpty[dayIdx] = false;
  });
  return { rowEmpty, colEmpty };
}

describe('Courses.vue - rowEmpty & colEmpty', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('all true when schedule is empty', () => {
    const mockUserData = makeMockUserData([]);
    const wrapper = mount(Courses, {
      global: { provide: { userData: mockUserData } },
    });

    expect(Array.isArray(wrapper.vm.rowEmpty)).toBe(true);
    expect(wrapper.vm.rowEmpty).toHaveLength(12);
    expect(wrapper.vm.colEmpty).toHaveLength(7);

    expect(wrapper.vm.rowEmpty.every(v => v === true)).toBe(true);
    expect(wrapper.vm.colEmpty.every(v => v === true)).toBe(true);

    wrapper.unmount();
  });

  it('detects single course at 周一 第1节 (index 0)', () => {
    const mockUserData = makeMockUserData([0]);
    const wrapper = mount(Courses, {
      global: { provide: { userData: mockUserData } },
    });

    const expected = expectedRowCol([0]);
    expect(wrapper.vm.rowEmpty).toEqual(expected.rowEmpty);
    expect(wrapper.vm.colEmpty).toEqual(expected.colEmpty);

    // 额外逐项断言
    expect(wrapper.vm.rowEmpty[0]).toBe(false);
    for (let i = 1; i < 12; i++) expect(wrapper.vm.rowEmpty[i]).toBe(true);
    expect(wrapper.vm.colEmpty[0]).toBe(false);
    for (let j = 1; j < 7; j++) expect(wrapper.vm.colEmpty[j]).toBe(true);

    wrapper.unmount();
  });

  it('detects multiple courses across periods and days', () => {
    const indices = [8, 20]; // index 8 -> period2 day1 ; index20 -> period3 day6
    const mockUserData = makeMockUserData(indices);
    const wrapper = mount(Courses, {
      global: { provide: { userData: mockUserData } },
    });

    const expected = expectedRowCol(indices);
    expect(wrapper.vm.rowEmpty).toEqual(expected.rowEmpty);
    expect(wrapper.vm.colEmpty).toEqual(expected.colEmpty);

    // 具体检查
    expect(wrapper.vm.rowEmpty[1]).toBe(false); // period 2
    expect(wrapper.vm.rowEmpty[2]).toBe(false); // period 3
    expect(wrapper.vm.colEmpty[1]).toBe(false); // 周二 (dayIdx 1)
    expect(wrapper.vm.colEmpty[6]).toBe(false); // 周日 (dayIdx 6)

    wrapper.unmount();
  });
});