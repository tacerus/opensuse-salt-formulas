describe file('/etc/salt/grains') do
  it { should exist }
  its('owner') { should match('root') }
end

describe yaml('/etc/salt/grains') do
  its('snack') { should eq 'peanuts' }
  its(['treats', 0]) { should eq 'chocolate' }
  its(['treats', 1]) { should eq 'candy' }
end
