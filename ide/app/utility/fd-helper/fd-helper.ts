export class FakeFormData {
  private form: HTMLFormElement;

  constructor(form: HTMLFormElement) {
    this.form = form;
  }

  get(key: string) {
    const elements = this.form.querySelectorAll(`[name="${ key }"]`);
    
    if (elements.length > 1) {
      return Array.from(elements)
        .map((element) => $(element).val());
    }
    else if (elements.length === 1) {
      return $(elements[0]).val();
    }
    else {
      return null;
    }
  }

  set(key: string, value: any) {
    const element = this.form.querySelector(`[name="${ key }"]`);
    if (element === null) {
      $(this.form).append(`<input type="hidden" name="${ key }" value="${ value }">`);
    }
    else {
      $(element).val(value);
    }
  }

  build() {
    return new FormData(this.form);
  }
}
