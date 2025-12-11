import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Note from '@/component/views/Note.vue';
import api from '@/api';

// Mock the API module
vi.mock('@/api', () => ({
  default: {
    getNoteFiles: vi.fn(),
    EditCourse: vi.fn(),
    EditNote: vi.fn(),
  },
  EditNote: vi.fn(),
}));

describe('Note.vue', () => {
  let wrapper;
  const mockUserData = {
    userId: 'user123',
    courses: [
      {
        name: 'Course A',
        tags: ['Tag1'],
        myNotes: [
          { name: 'Note 1', file: 'file1.pdf' },
          { name: 'Note 2', file: 'file2.pdf' },
        ],
      },
      {
        name: 'Course B',
        tags: ['Tag2'],
        myNotes: [],
      },
    ],
  };

  const mockFileview = { value: false };
  const mockFilepath = { value: '' };

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    mockFileview.value = false;
    mockFilepath.value = '';

    // Mock document.getElementById to prevent errors and verify calls
    const mockElement = {
      classList: {
        contains: vi.fn().mockReturnValue(false),
        remove: vi.fn(),
        add: vi.fn(),
      },
      style: {},
      querySelector: vi.fn().mockReturnValue({ textContent: 'Course A' }),
    };
    
    // Mock getElementsByClassName for SearchHandler
    const mockCourseItem = {
      querySelector: vi.fn().mockReturnValue({ textContent: 'Course A' }),
      style: { display: '' }
    };
    
    vi.spyOn(document, 'getElementById').mockReturnValue(mockElement);
    vi.spyOn(document, 'getElementsByClassName').mockReturnValue([mockCourseItem]);

    wrapper = mount(Note, {
      attachTo: document.body, // Attach to DOM for document.getElementById to work if needed, though we mocked it
      global: {
        provide: {
          userData: mockUserData,
          fileview: mockFileview,
          filepath: mockFilepath,
        },
      },
    });
  });

  afterEach(() => {
    wrapper.unmount();
    vi.restoreAllMocks();
  });

  it('renders course list correctly', () => {
    const courseNames = wrapper.findAll('.course-name');
    expect(courseNames).toHaveLength(2);
    expect(courseNames[0].text()).toBe('Course A');
    expect(courseNames[1].text()).toBe('Course B');
  });

  it('toggles notes list visibility', async () => {
    // Find the toggle button (2nd button in the first course item)
    // Buttons: Rename, Toggle, Delete
    const toggleBtn = wrapper.findAll('button')[1];
    await toggleBtn.trigger('click');

    expect(document.getElementById).toHaveBeenCalledWith('icon-0');
    expect(document.getElementById).toHaveBeenCalledWith('notes-list-0');
  });

  it('filters courses based on search input', async () => {
    const searchInput = wrapper.find('#searchinput');
    await searchInput.setValue('Course A');
    await searchInput.trigger('input');

    // Since SearchHandler uses document.getElementsByClassName directly,
    // we verify our spy was called or check the logic if possible.
    // The component modifies the style of elements found by getElementsByClassName.
    // We can check if getElementsByClassName was called.
    expect(document.getElementsByClassName).toHaveBeenCalledWith('course-item');
  });

  it('handles note file display', async () => {
    api.getNoteFiles.mockResolvedValue({ files: [{ url: 'http://example.com/file.pdf' }] });

    // Find the note name span. Structure: li > span > span(clickable)
    // We can find by text to be sure
    const noteSpans = wrapper.findAll('li span span');
    const noteItem = noteSpans.find(s => s.text() === 'Note 1');
    
    await noteItem.trigger('click');

    expect(api.getNoteFiles).toHaveBeenCalledWith({
      userId: 'user123',
      lessonName: 'Course A',
      noteName: 'Note 1',
    });

    // Wait for promise resolution
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(mockFileview.value).toBe(true);
    expect(mockFilepath.value).toBe('http://example.com/file.pdf');
  });

  it('handles course name editing', async () => {
    const courseName = wrapper.find('.course-name');
    await courseName.trigger('dblclick');

    // After dblclick, the span is replaced by an input
    // There is a search input at the top, so we need to find the correct input.
    // The edit input has class 'border-gray-300' and is inside the course item.
    const inputs = wrapper.findAll('input[type=\"text\"]');
    // inputs[0] is search, inputs[1] should be the edit input for the course
    const editInput = inputs[1];

    await editInput.setValue('New Course Name');
    await editInput.trigger('blur');

    expect(api.EditCourse).toHaveBeenCalledWith({
      userId: 'user123',
      oldName: 'Course A',
      newName: 'New Course Name',
    });
  });
});
