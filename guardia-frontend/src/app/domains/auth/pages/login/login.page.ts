import { Component } from '@angular/core';
import { LoginFormComponent } from './login-form.component';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [LoginFormComponent],
  template: `
    <div class="min-h-screen flex items-center justify-center p-4">
      <app-login-form class="w-full" />
    </div>
  `
})
export class LoginPageComponent {}
