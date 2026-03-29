import { promises as fs } from 'node:fs';
import path from 'node:path';
import { COMPANY_LOGO_DOMAINS } from '../src/utils/companies.js';

const outDir = path.resolve('public/company-logos');
await fs.mkdir(outDir, { recursive: true });

const entries = Object.entries(COMPANY_LOGO_DOMAINS);
const failed = [];

const alternateDomains = {
    tcs: ['tcsion.com', 'tataconsultancyservices.com'],
    hcl: ['hcl.com', 'hclinfosystems.in'],
};

for (const [id, domain] of entries) {
    const outputFile = path.join(outDir, `${id}.png`);
    const domains = [domain, ...(alternateDomains[id] || [])];
    const sources = domains.flatMap((d) => [
        `https://logo.clearbit.com/${d}`,
        `https://www.google.com/s2/favicons?domain=${d}&sz=128`,
    ]);

    let saved = false;

    for (const url of sources) {
        try {
            const response = await fetch(url, {
                headers: { 'User-Agent': 'Mozilla/5.0' },
            });
            if (!response.ok) continue;

            const data = Buffer.from(await response.arrayBuffer());
            if (data.length < 100) continue;

            await fs.writeFile(outputFile, data);
            saved = true;
            break;
        } catch {
            // Try next source.
        }
    }

    if (!saved) {
        failed.push({ id, domain });
    }
}

console.log(`Downloaded logos: ${entries.length - failed.length}/${entries.length}`);
if (failed.length > 0) {
    console.log('Failed logos:');
    for (const item of failed) {
        console.log(`- ${item.id} (${item.domain})`);
    }
}
