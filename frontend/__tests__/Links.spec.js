import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import Links from '@/component/views/Links.vue';
import { UpdateLinkCategory } from '@/api';

// Mock api module
vi.mock('@/api', () => ({
  UpdateLinkCategory: vi.fn(),
}));

describe('Links.vue', () => {
  let wrapper;
  const mockUserData = {
    value: {
      id: 'user123',
      linkCategories: []
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset userData mock
    mockUserData.value.linkCategories = [];
    
    // Mock window.open and window.alert
    vi.spyOn(window, 'open').mockImplementation(() => {});
    vi.spyOn(window, 'alert').mockImplementation(() => {});
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    wrapper = mount(Links, {
      global: {
        provide: {
          userData: mockUserData
        }
      }
    });
  });

  afterEach(() => {
    wrapper.unmount();
    vi.restoreAllMocks();
  });

  it('renders default links when userData is empty', () => {
    expect(wrapper.text()).toContain('学术研究与资料库');
    expect(wrapper.text()).toContain('Google Scholar');
  });

  it('uses userData links when available', async () => {
    const customLinks = [
      {
        category: 'Custom Category',
        icon: '🧪',
        links: [{ name: 'Custom Link', url: 'http://test.com', desc: 'Test Desc', isTrusted: true }]
      }
    ];
    
    mockUserData.value.linkCategories = customLinks;
    
    // Re-mount to pick up new provided data
    wrapper = mount(Links, {
      global: {
        provide: {
          userData: mockUserData
        }
      }
    });

    expect(wrapper.text()).toContain('Custom Category');
    expect(wrapper.text()).toContain('Custom Link');
  });

  it('adds a new link correctly', async () => {
    // 1. Open Add Link Panel
    const addLinkBtn = wrapper.findAll('button').find(b => b.text().includes('添加新链接'));
    expect(addLinkBtn.exists()).toBe(true);
    await addLinkBtn.trigger('click');

    // 2. Fill Form
    const nameInput = wrapper.find('#link-name');
    const urlInput = wrapper.find('#link-url');
    const categorySelect = wrapper.find('#link-category');

    expect(nameInput.exists()).toBe(true);
    
    await nameInput.setValue('New Vue Link');
    await urlInput.setValue('https://vuejs.org');
    
    // Select the first category available
    const options = categorySelect.findAll('option');
    await categorySelect.setValue(options[0].element.value);

    // 3. Submit
    const forms = wrapper.findAll('form');
    const addLinkForm = forms.find(f => f.find('#link-name').exists());
    await addLinkForm.trigger('submit');

    // 4. Verify API call
    // Since we are using default data (userData is empty initially), the component might update local state first
    // But if we mock userData to have structure, it should call API.
    // In the component: if (userData.value?.linkCategories) -> UpdateLinkCategory
    // Our mockUserData has linkCategories = [], so it should trigger.
    
    expect(UpdateLinkCategory).toHaveBeenCalled();
    const callArgs = UpdateLinkCategory.mock.calls[0][0];
    expect(callArgs.userId).toBe('user123');
    // Check if the new link is in the payload
    const category = callArgs.linkCategories.find(c => c.category === options[0].element.value);
    expect(category.links).toEqual(expect.arrayContaining([
      expect.objectContaining({ name: 'New Vue Link', url: 'https://vuejs.org' })
    ]));
  });

  it('handles untrusted link navigation with trust option', async () => {
    // 1. Find an untrusted link (from default data)
    // "一个不信任的网站" is in the default data
    const untrustedLinkName = '一个不信任的网站';
    const linkElement = wrapper.findAll('a').find(a => a.text().includes(untrustedLinkName));
    expect(linkElement.exists()).toBe(true);

    // 2. Click to open modal
    await linkElement.trigger('click');

    // 3. Check Modal
    const modal = wrapper.find('.fixed.z-\\[100\\]'); // Tailwind class for modal overlay
    expect(modal.exists()).toBe(true);
    expect(modal.text()).toContain('外部链接提醒');

    // 4. Check "Trust" checkbox
    const trustCheckbox = wrapper.find('#modal-trust-checkbox');
    expect(trustCheckbox.exists()).toBe(true);
    await trustCheckbox.setValue(true);

    // 5. Confirm navigation
    const confirmBtn = wrapper.findAll('button').find(b => b.text().includes('确认跳转'));
    await confirmBtn.trigger('click');

    // 6. Verify actions
    expect(window.open).toHaveBeenCalled();
    // Since we checked "Trust", UpdateLinkCategory should be called to save the new state
    expect(UpdateLinkCategory).toHaveBeenCalled();
  });
});
