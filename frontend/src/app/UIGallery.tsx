import React from 'react';
import { Button } from '../shared/ui/Button';
import { Input } from '../shared/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../shared/ui/Card';

export function UIGallery() {
  return (
    <div style={{ padding: '40px', maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '40px' }}>
      <div>
        <h1 style={{ marginBottom: '8px' }}>UI Component Gallery</h1>
        <p className="text-secondary">A visual reference of the FlowForge design system primitives.</p>
      </div>

      <section>
        <h2 style={{ marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>Buttons</h2>
        <div className="flex items-center gap-4" style={{ marginBottom: '16px' }}>
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
        </div>
        <div className="flex items-center gap-4">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>

      <section>
        <h2 style={{ marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>Inputs</h2>
        <div style={{ maxWidth: '300px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <Input placeholder="Default input..." />
          <Input placeholder="Disabled input..." disabled />
        </div>
      </section>

      <section>
        <h2 style={{ marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>Cards & Glassmorphism</h2>
        <Card style={{ maxWidth: '400px' }}>
          <CardHeader>
            <CardTitle>Project Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-secondary" style={{ marginBottom: '16px' }}>This is an example of the glassmorphism surface that will be used throughout the app.</p>
            <Button variant="primary">View Details</Button>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
