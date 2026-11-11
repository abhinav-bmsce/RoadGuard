import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatCard } from '../components/StatCard';
import { DamageCard } from '../components/DamageCard';
import { DamageInstance } from '../types';
import { ShieldCheck } from 'lucide-react';

describe('SeverityBadge Component', () => {
  it('renders Low severity badge with score correctly', () => {
    render(<SeverityBadge level="Low" score={18.4} />);
    expect(screen.getByText('Low / Minor')).toBeInTheDocument();
    expect(screen.getByText('18.4')).toBeInTheDocument();
  });

  it('renders High hazard badge correctly', () => {
    render(<SeverityBadge level="High" score={85.2} />);
    expect(screen.getByText('High Hazard')).toBeInTheDocument();
    expect(screen.getByText('85.2')).toBeInTheDocument();
  });
});

describe('StatCard Component', () => {
  it('renders metric title and value', () => {
    render(
      <StatCard
        title="Total Inspections"
        value={142}
        subtitle="Audited frames"
        icon={<ShieldCheck data-testid="shield-icon" />}
      />
    );
    expect(screen.getByText('Total Inspections')).toBeInTheDocument();
    expect(screen.getByText('142')).toBeInTheDocument();
    expect(screen.getByText('Audited frames')).toBeInTheDocument();
  });
});

describe('DamageCard Component', () => {
  it('renders damage instance with confidence and area', () => {
    const mockDamage: DamageInstance = {
      class_id: 3,
      class_name: 'D40_Pothole',
      confidence: 0.88,
      bbox: { xmin: 50, ymin: 100, xmax: 250, ymax: 300 },
      area_ratio: 0.097,
      instance_severity: 78.5,
      severity_tag: 'High',
    };

    render(<DamageCard damage={mockDamage} index={0} />);
    expect(screen.getByText('Pothole')).toBeInTheDocument();
    expect(screen.getByText('D40')).toBeInTheDocument();
    expect(screen.getByText('Conf: 88.0%')).toBeInTheDocument();
    expect(screen.getByText('Area: 9.70%')).toBeInTheDocument();
  });
});

